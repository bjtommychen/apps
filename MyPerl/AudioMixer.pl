#!/usr/bin/perl   

my @buff; # = (0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0); 
my $buf;
my $destfile = $ARGV[1];
my $offsetbase  = 0;
my $rlen = 1;
########### Start #############
if ($ARGV[0] eq "")
{
	print "AudioMixer v0.1 -- by Tommy Chen \n";
	print "Usage: perl input_4_channel_pcm output_mixed_mono_pcm \n";
	print "\n";

}
if ($ARGV[0] eq "")
{
	die "\n";	
}

open (FILEIN, "<$ARGV[0]") or die "Can't open input file $!";
open (FILEOUT, ">$destfile") or die "Can't open output file $!";
binmode FILEIN;
binmode FILEOUT;

read(FILEIN, $buf, 44);		#0x2c, skip wav header

while($rlen > 0)
{
	for ($j = 0; $j < 4; $j++)
	{

		if ($rlen = read(FILEIN, $buf, 8*8000)) 
		{ 
		@buff = split("", $buf);
		$offset = $offsetbase;
			for ($i = 0; $i < 8000; $i++)
			{
				print FILEOUT $buff[$offset+0]; 
				print FILEOUT $buff[$offset+1];
				#$offset += 2;	#normal 
				#$offset += 10; #skip 10 bytes per sample
				$offset += 8;   #same channel.
			}

		#print "."; 
		}

		$offsetbase += 2;
		if ($offsetbase > 3*2)
		{
			$offsetbase = 0;
		}

	}	#for j

}

