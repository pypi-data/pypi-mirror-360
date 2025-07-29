<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
<html>
 <head><title>A sample blog</title></head>

 <body>
<?php
function params_get($which) {
    if(isset($_GET[$which])) {
        $v = $_GET[$which];
        if($v!="") return $v;
    }
    return null;
}

function tinyReplace($format, $values) {
    $ret = $format;
    foreach ($values as $key => $value) {
        if(!is_string($value)) {
            continue;
        }
        $ret = str_replace("%".$key."%", $value, $ret);
    }
    return $ret;
}

function writeItemsAsList($items, $format) {
    echo("<ul class=\"entrylist\">\n");
    foreach ($items as $e) {
        echo(tinyReplace($format, $e));
    }
    echo("</ul>\n");
}

function sortItems($items, $field, $dir=SORT_DESC) {
    $tmp = array();
    foreach ($items as $key => $row) {
        $tmp[$key] = $row->$field;
    }
    array_multisort($tmp, $dir, $items);
    return $items;
}

function toArray($db) {
    $ret = array();
    foreach ($db as $key => $row) {
        $ret[$key] = $row;
    }
    return $ret;
}

function filterItemsByTopic($items, $value) {
    $ret = array();
    $key = "topics";
    foreach ($items as $ekey => $row) {
        $found = 0;
        foreach ($row->topics as $topic) {
            if($topic==$value) {
                $found = 1;
            }
        }
        if($found==1) {
            $ret[$ekey] = $row;
        }
    }
    return $ret;
}


// this is only responsible for showing lists or menus
// the blog entries themselves exist as pre-built static pages
$toShow = params_get("show"); // "items", "topics"
if($toShow==null) $toShow = "items";
$db = file_get_contents("entries.json");
$db = json_decode($db);
foreach ($db as $entry) {
    $entry->idate = date_create($entry->date);
}
if($toShow=="topics") {
	// show (all) topics
    echo("<h1>Covered Topics</h1>\n");
    echo("<div>");
    $topics = array();
    foreach ($db as $entry) {
        foreach ($entry->topics as $topic) {
            $topics[$topic] = array("title"=>$topic);
        }
    }
    writeItemsAsList($topics, "<li><a href=\"index.php?topic=%title%\">%title%</a></li>\n");
    echo("</div>");
} else {
    $topicFilter = params_get("topic");
    if($topicFilter==null) {
        echo("<h1>Most recent entries</h1>\n");
    } else {
        echo("<h1>Most recent entries for topic '".$topicFilter."'</h1>\n");
    }
    echo("<div><p>");
    $items = toArray($db);
    if($topicFilter!=null) {
        $items = filterItemsByTopic($items, $topicFilter);
    }
    $items = sortItems($items, "idate");
    writeItemsAsList($items, "<li><a href=\"%filename%\">%title%</a> (%date%)<br/>%abstract% (<a href=\"%filename%\">read more</a>)</li>\n");
    echo("</p></div>");
}
?>
 </body>
</html>


