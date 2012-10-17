#!/usr/bin/perl   
use Cwd;   

########### CONFIG PARAMETERS###############
my $infile  = $ARGV[0];
my $outfile = $ARGV[1]; 
my $valstr;
my $val;

#control
my $mydebug = 0;	# 1: if just print the commands.
 

#######################################
my $currdir   =   getcwd();   
 
my $i = 0;
my $cmd;

########### Start #############
if (1) #($ARGV[0] eq "")
{
	print "mpeg_iso_pcm_to_bin.pl v0.1 -- by Tommy Chen \n";
	print "Target: Convert MPEG ISO layer1/layer2/*.pcm(ASCII mode) into 16bit BIN mode. \n";
	print "Usage: perl mpeg_iso_pcm_to_bin.pl <in.pcm> <out.bin>\n";
	print "\n";
}

if ($ARGV[0] eq "")
{
	die "\n";	
}

if ($ARGV[1] eq "")
{
	$outfile = "out.bin";
}

print "Output to $outfile !\n";

open(INPUTFILE, "<$infile");
open(OUTPUTFILE,">$outfile");
binmode(OUTPUTFILE);

my(@lines) = <INPUTFILE>;      

foreach my $line (@lines) 
{ 
	my $v_hi, $v_lo;
	$i += 1;
#	print "No.$i, $line";
	$valstr = lc(substr($line, 0,4));	
	$v_hi = lc(substr($line, 0,2));	
	$v_lo = lc(substr($line, 2,2));	
#	print sprintf("0x%02x, $valstr, $v_hi, $v_lo. \n",$i);
#	print OUTPUTFILE pack("H*",sprintf("%04x",$i));
#	print OUTPUTFILE pack("H*", $valstr);
	print OUTPUTFILE pack("H*", $v_lo);
	print OUTPUTFILE pack("H*", $v_hi);
}

print "Done !";

#die "\n";


