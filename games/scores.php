<?php
/*
 * Shared top 10 for Clown Invaders and Beat The Clown.
 *
 *   GET  scores.php?game=invaders        -> {"ok":true,"top":[...]}
 *   POST scores.php  (JSON body)         -> {"ok":true,"rank":3,"top":[...]}
 *        {"game":"invaders","name":"MATHS","country":"BE","score":1234,"level":2,"duration":95.4}
 *   Admin: open scores.php?admin=YOUR_KEY in a browser to see and delete scores.
 *
 * Scores are stored in data/scores.sqlite (the data folder is locked by its .htaccess).
 * Only the chosen player name, country flag, score, level/speed, play time and date are stored.
 * To stop flooding, a scrambled (hashed) form of the visitor's IP address is kept
 * for at most one hour and then deleted. Needs PHP 7.4+ with PDO SQLite.
 */

// Set your own secret to switch on the admin page. Leave empty to keep it off.
const ADMIN_KEY = '';

const GAMES = ['invaders' => 'Clown Invaders', 'beat' => 'Beat The Clown'];
const TOP_N = 10;
const KEEP_PER_GAME = 1000;       // older low scores beyond this are trimmed
const MAX_POSTS_PER_MINUTE = 6;   // per visitor

$dataDir = __DIR__ . '/data';

function out($data, $code = 200) {
    http_response_code($code);
    header('Content-Type: application/json; charset=utf-8');
    header('Cache-Control: no-store');
    echo json_encode($data, JSON_UNESCAPED_UNICODE);
    exit;
}

function db($dataDir) {
    if (!is_dir($dataDir)) {
        @mkdir($dataDir, 0755, true);
    }
    if (!file_exists("$dataDir/.htaccess")) {
        @file_put_contents("$dataDir/.htaccess",
            "Require all denied\n<IfModule !mod_authz_core.c>\nDeny from all\n</IfModule>\n");
    }
    $pdo = new PDO('sqlite:' . $dataDir . '/scores.sqlite');
    $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
    $pdo->setAttribute(PDO::ATTR_DEFAULT_FETCH_MODE, PDO::FETCH_ASSOC);
    $pdo->exec('PRAGMA busy_timeout = 3000');
    $pdo->exec('CREATE TABLE IF NOT EXISTS scores (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        game TEXT NOT NULL,
        name TEXT NOT NULL,
        score INTEGER NOT NULL,
        level INTEGER NOT NULL DEFAULT 1,
        duration REAL NOT NULL DEFAULT 0,
        created INTEGER NOT NULL)');
    // add the country column to databases made before flags existed
    $cols = $pdo->query('PRAGMA table_info(scores)')->fetchAll();
    if (!in_array('country', array_column($cols, 'name'), true)) {
        $pdo->exec("ALTER TABLE scores ADD COLUMN country TEXT NOT NULL DEFAULT ''");
    }
    $pdo->exec('CREATE INDEX IF NOT EXISTS scores_game ON scores (game, score DESC)');
    $pdo->exec('CREATE TABLE IF NOT EXISTS hits (who TEXT NOT NULL, ts INTEGER NOT NULL)');
    return $pdo;
}

// Best score per name, highest first.
function top($pdo, $game) {
    $st = $pdo->prepare('SELECT s.name, s.country, s.score, s.level, s.created
        FROM scores s
        WHERE s.game = :g AND s.id = (
            SELECT t.id FROM scores t WHERE t.game = s.game AND t.name = s.name
            ORDER BY t.score DESC, t.created ASC LIMIT 1)
        ORDER BY s.score DESC, s.created ASC
        LIMIT ' . TOP_N);
    $st->execute([':g' => $game]);
    $rows = $st->fetchAll();
    foreach ($rows as &$r) {
        $r['score'] = (int)$r['score'];
        $r['level'] = (int)$r['level'];
        $r['date'] = gmdate('Y-m-d', (int)$r['created']);
        unset($r['created']);
    }
    return $rows;
}

// Rank among players (each name counted once, by their best score).
function rank($pdo, $game, $name, $score) {
    $st = $pdo->prepare('SELECT COUNT(*) FROM (
        SELECT name, MAX(score) AS best FROM scores WHERE game = :g AND name <> :n GROUP BY name
        ) WHERE best > :s');
    $st->bindValue(':g', $game);
    $st->bindValue(':n', $name);
    $st->bindValue(':s', (int)$score, PDO::PARAM_INT);   // as a number, so SQLite compares correctly
    $st->execute();
    return (int)$st->fetchColumn() + 1;
}

function visitorHash($dataDir) {
    $saltFile = "$dataDir/salt.txt";
    $salt = @file_get_contents($saltFile);
    if (!$salt) {
        $salt = bin2hex(random_bytes(16));
        @file_put_contents($saltFile, $salt);
    }
    $ip = isset($_SERVER['REMOTE_ADDR']) ? $_SERVER['REMOTE_ADDR'] : '';
    return hash('sha256', $salt . '|' . $ip);
}

// Rough upper limits, so obviously impossible scores are refused.
function plausible($game, $score, $level, $duration) {
    if ($game === 'invaders') {
        // pies, bear bonuses, speed-up and round bonuses: well under 600 points per second
        return $score <= 600 * $duration + 2000 && $level <= 1 + $duration / 5;
    }
    // Beat The Clown: level k scores at most 10000 x k, and every level takes over 5 seconds
    $cleared = max(0, $level - 1);
    return $score <= 10000 * $cleared * ($cleared + 1) / 2 && $duration >= $cleared * 5;
}

try {
    $pdo = db($dataDir);
} catch (Exception $e) {
    out(['ok' => false, 'error' => 'Score storage is not available'], 500);
}

/* ---------- admin page ---------- */
if (isset($_REQUEST['admin'])) {
    if (ADMIN_KEY === '' || !hash_equals(ADMIN_KEY, (string)$_REQUEST['admin'])) {
        http_response_code(403);
        exit('Admin page is off or the key is wrong.');
    }
    if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['delete'])) {
        $pdo->prepare('DELETE FROM scores WHERE id = ?')->execute([(int)$_POST['delete']]);
    }
    $key = htmlspecialchars(ADMIN_KEY, ENT_QUOTES);
    header('Content-Type: text/html; charset=utf-8');
    echo '<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
       . '<title>Scores admin</title><style>body{font:14px system-ui;margin:16px}table{border-collapse:collapse}'
       . 'td,th{padding:4px 10px;border-bottom:1px solid #ddd;text-align:left}button{cursor:pointer}</style>';
    foreach (GAMES as $g => $label) {
        echo '<h2>' . htmlspecialchars($label) . '</h2><table><tr><th>Country</th><th>Name</th><th>Score</th><th>Level</th><th>Time</th><th>Date</th><th></th></tr>';
        $st = $pdo->prepare('SELECT * FROM scores WHERE game = ? ORDER BY score DESC LIMIT 200');
        $st->execute([$g]);
        foreach ($st as $r) {
            echo '<tr><td>' . htmlspecialchars($r['country']) . '</td><td>' . htmlspecialchars($r['name']) . '</td><td>' . (int)$r['score'] . '</td><td>' . (int)$r['level']
               . '</td><td>' . round($r['duration']) . 's</td><td>' . gmdate('Y-m-d H:i', (int)$r['created']) . '</td><td>'
               . '<form method="post"><input type="hidden" name="admin" value="' . $key . '">'
               . '<button name="delete" value="' . (int)$r['id'] . '">Delete</button></form></td></tr>';
        }
        echo '</table>';
    }
    exit;
}

/* ---------- read the top 10 ---------- */
if ($_SERVER['REQUEST_METHOD'] === 'GET') {
    $game = isset($_GET['game']) ? $_GET['game'] : '';
    if (!isset(GAMES[$game])) {
        out(['ok' => false, 'error' => 'Unknown game'], 400);
    }
    out(['ok' => true, 'top' => top($pdo, $game)]);
}

/* ---------- save a score ---------- */
if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    out(['ok' => false, 'error' => 'Use GET or POST'], 405);
}
$in = json_decode(file_get_contents('php://input'), true);
if (!is_array($in)) {
    out(['ok' => false, 'error' => 'Bad request'], 400);
}
$game = isset($in['game']) ? (string)$in['game'] : '';
$name = isset($in['name']) ? strtoupper(trim(preg_replace('/\s+/u', ' ', (string)$in['name']))) : '';
$country = isset($in['country']) ? strtoupper((string)$in['country']) : '';
$score = isset($in['score']) ? (int)$in['score'] : -1;
$level = isset($in['level']) ? (int)$in['level'] : 1;
$duration = isset($in['duration']) ? (float)$in['duration'] : 0;

if (!isset(GAMES[$game])) out(['ok' => false, 'error' => 'Unknown game'], 400);
if (!preg_match('/^[\p{L}\p{N} @._!\-]{1,8}$/u', $name)) out(['ok' => false, 'error' => 'Name must be 1 to 8 letters or numbers'], 400);
if ($country !== '' && !preg_match('/^[A-Z]{2}$/', $country)) $country = '';
if ($score < 1 || $score > 100000000) out(['ok' => false, 'error' => 'Score out of range'], 400);
if ($level < 1 || $level > 1000 || $duration < 1 || $duration > 6 * 3600) out(['ok' => false, 'error' => 'Run out of range'], 400);
if (!plausible($game, $score, $level, $duration)) out(['ok' => false, 'error' => 'That score does not look possible'], 400);

// flood control: a few saves per minute per visitor; hashes are deleted after an hour
$now = time();
$who = visitorHash($dataDir);
$pdo->prepare('DELETE FROM hits WHERE ts < ?')->execute([$now - 3600]);
$st = $pdo->prepare('SELECT COUNT(*) FROM hits WHERE who = ? AND ts > ?');
$st->execute([$who, $now - 60]);
if ((int)$st->fetchColumn() >= MAX_POSTS_PER_MINUTE) {
    out(['ok' => false, 'error' => 'Too many scores at once, try again in a minute'], 429);
}
$pdo->prepare('INSERT INTO hits (who, ts) VALUES (?, ?)')->execute([$who, $now]);

$pdo->prepare('INSERT INTO scores (game, name, country, score, level, duration, created) VALUES (?, ?, ?, ?, ?, ?, ?)')
    ->execute([$game, $name, $country, $score, $level, round($duration, 1), $now]);

// keep the table small
$pdo->prepare('DELETE FROM scores WHERE game = :g AND id NOT IN (
    SELECT id FROM scores WHERE game = :g ORDER BY score DESC LIMIT ' . KEEP_PER_GAME . ')')
    ->execute([':g' => $game]);

out(['ok' => true, 'rank' => rank($pdo, $game, $name, $score), 'top' => top($pdo, $game)]);
