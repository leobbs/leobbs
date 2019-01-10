#####################################################
#  LEO SuperCool BBS / LeoBBS X / 雷傲极酷超级论坛  #
#####################################################
# 基于山鹰(糊)、花无缺制作的 LB5000 XP 2.30 免费版  #
#   新版程序制作 & 版权所有: 雷傲科技 (C)(R)2004    #
#####################################################
#      主页地址： http://www.LeoBBS.com/            #
#      论坛地址： http://bbs.LeoBBS.com/            #
#####################################################

use strict;
use warnings;
use diagnostics;

$addme = qq~<a href=attachment.cgi?forum=$in_forum&topic=$in_topic&postno=$editpostnumber&type=.$up_ext><img src=$imagesurl/icon/$filetype.gif border=0 width=16><a> <a href=attachment.cgi?forum=$in_forum&topic=$in_topic&postno=$editpostnumber&type=.$up_ext>该主题有一个 BitTorrent 格式的文件，按此下载</a> (共 $fileinfo[7] 字节)<br>~;

open(FILE, "${imagesdir}$usrdir/$in_forum/$up_name.$up_ext.btfile");
sysread(FILE, $btinfo, (stat(FILE))[7]);
close(FILE);
$btinfo =~ s/\r//isg;

chomp($btinfo);

if (length($btinfo) <= 50) {
    eval("use BTINFO;");
    if ($@ eq "") {
        $/ = "";
        open(FILE, "${imagesdir}$usrdir/$in_forum/$up_name.$up_ext");
        binmode(FILE);
        my $bufferall = <FILE>;
        close(FILE);
        $/ = "\n";
        my $btfileinfo = process_file($bufferall);
        my (undef, $hash, $announce) = split(/\n/, $btfileinfo);
        open(FILE, ">${imagesdir}$usrdir/$in_forum/$up_name.$up_ext.btfile");
        print FILE "$btfileinfo\|$seedinfo";
        close(FILE);
        $btinfo = "$btfileinfo\|$seedinfo";
    }
}

my ($btfileinfo, $hash, $seedinfo) = split(/\n/, $btinfo);
($announce, $seeds, $leeches, $downloaded) = split(/\|/, $seedinfo);
if ($seeds eq "") {
    $seeds = "未知";
    $leeches = "未知";
    $downloaded = "未知";
}

my @btfileinfo = split(/\t/, $btfileinfo);
$addme .= qq~
<script>
function ShowMore(){
for (var i = 0; i < AFILE.length; i++){var e = AFILE[i];e.style.display = "";}
var _S = BFILE;
_S.style.display = "none";
}
</script>
<ul><table cellSpacing=1 cellPadding=4 bgColor=$tablebordercolor width=280><tr bgColor=$titlecolor><td align=middle nowrap><font color=$titlefontcolor>文件名</td><td align=middle nowrap><font color=$titlefontcolor>文件大小</td></tr>~;

my $allfilelength = 0;
my $counters = 0;
foreach (@btfileinfo) {
    next if ($_ eq "");
    $counters++;
    if ($counters % 2 == 1) {
        $postbackcolor1 = $postcolorone;
        $postfontcolor1 = $postfontcolorone;
    }
    else {
        $postbackcolor1 = $postcolortwo;
        $postfontcolor1 = $postfontcolortwo;
    }
    my ($file_name, $filelength) = split(/\|/, $_);
    $allfilelength += $filelength;

    $lbsd = 'Bytes';
    if ($filelength > 1024) {
        $filelength /= 1024;
        $lbsd = 'KB';
    }
    if ($filelength > 1024) {
        $filelength /= 1024;
        $lbsd = 'MB';
    }
    if ($filelength > 1024) {
        $filelength /= 1024;
        $lbsd = 'GB';
    }
    $filelength = sprintf("%6.2f", $filelength) . " $lbsd";

    if ($counters eq 8) {$addme1 .= qq~ id=AFILE style=display:none~;}

    $addme .= qq~<tr bgColor=$postbackcolor1 $addme1><td align=middle nowrap><font color=$postfontcolor1>$file_name</td><td align=middle nowrap><font color=$postfontcolor1>$filelength</td></tr>~;
}
if ($counters >= 8) {$addme .= qq~<tr bgColor=$postbackcolor1 id=BFILE style=display:""><td align=right nowrap colspan=2><span style=CURSOR:hand onclick=ShowMore()><font color=$postfontcolor1 title=显示所有文件>更多...</font></span>&nbsp;</td></tr>~;}

($announce, $seeds, $leeches, $downloaded) = split(/\|/, $seedinfo);
if ($seeds eq "") {
    $seeds = "未知";
    $leeches = "未知";
    $downloaded = "未知";
}
$lbsd = 'Bytes';
if ($allfilelength > 1024) {
    $allfilelength /= 1024;
    $lbsd = 'KB';
}
if ($allfilelength > 1024) {
    $allfilelength /= 1024;
    $lbsd = 'MB';
}
if ($allfilelength > 1024) {
    $allfilelength /= 1024;
    $lbsd = 'GB';
}
$allfilelength = sprintf("%6.2f", $allfilelength) . " $lbsd";

$addme .= qq~<tr bgColor=$titlecolor><td align=right nowrap colspan=2>种子数：$seeds&nbsp;连接数：$leeches&nbsp;完成数：$downloaded&nbsp;<BR>[<a href=getbtinfo.cgi?forum=$in_forum&filename=$up_name target=_blank title="按此可获得即时的资料数据，如果显示出现\n白屏，可能是对方服务器无法连接。">本页面数据并非即时，如需要即时信息请按这里</a>]&nbsp;<br>总共有 $counters 个文件，内容共有 $allfilelength&nbsp;<br>URL: $announce&nbsp;<br></td></tr></table></ul>~;
1;