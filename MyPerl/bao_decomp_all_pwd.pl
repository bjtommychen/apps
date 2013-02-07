#!/usr/bin/perl   

	my($dir) = ".";
	my($file);
	my($zipext)="zip";
	my($rarext)="rar";
	my $cmd;
	my($tmpdir) = "tmp";
	opendir(DIR, $dir) || die "Unabel open $dir:$!";
	my(@lfiles) = grep {!/^\.\.?$/ } readdir(DIR);
	
	foreach $lfile (@lfiles)
	{	
		#if(-d $lfile)
		#	print "dir \n";
		if($lfile=~/$zipext/ || $lfile=~/$rarext/)
		{
			#print "\n\n*****************************************\nfile ", $lfile, "\n";
#			$cmd = "unrar  e -o+  -p- -pwww.bjzgks.com"." ".$lfile. " tmp";
#			$cmd = "wzunzip   ".$lfile. " tmp -s\"rlzys\"";
			$cmd = "wzunzip   ".$lfile. " tmp -s\"www.bjzgks.com\"";
#			print "cmd is ", $cmd, "\n";
#			print "run cmd ... ", $cmd;
			system ($cmd);
			
			#print "tmpdir file number is ", is_emptydir($tmpdir);
			if (filenum_in_dir($tmpdir)==0)
			{
				print "empty dir !!\n";
				print "\n\n*****************************************\nfile ", $lfile, "\n";
			}
			else
			{
				$cmd = "mv tmp/* done ";
				#print "run cmd ... ", $cmd;
				system($cmd);
				$cmd = "rm ".$lfile;
				system($cmd);
				print "\nrmove ", $lfile, "\n";
			}
		}
	}	
	
	
	#is_empty($dirname)==0 ¼´Îª¿ÕÄ¿Â¼
sub is_empty
 {
    open DIR, shift or die "$!\n";
    grep !/^\.\.?$/, readdir DIR;
}

sub filenum_in_dir
 {
	opendir(DIR, shift) || die "Unabel open $dir:$!";
  #	print shift;
    my(@tmp_files);
  #  open DIR, shift or die "aaaaaaaaaaaa $!\n";
    
    @tmp_files = grep !/^\.\.?$/, readdir DIR;
	foreach $tmpfile (@tmp_files)
	{
	#	print "file ", $tmpfile, "\n";		
	}
	return scalar(@tmp_files);
}