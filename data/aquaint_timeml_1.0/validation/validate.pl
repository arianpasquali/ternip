#!/usr/bin/perl# ========================================================================# validate.pl# ========================================================================## Use XML::Checker::Parser to validate TimeML files. Usage:##      perl validate.pl [-e <string>] <dir>## The optional -e option allows specification of an extension, only# files with that extension will be used as input. This script needs# to run from the directory it is in. Results are printed to standard# output.## The only lines that may need to be edited are##    my $DTD = 'timeml_1.2.1.dtd';#    my $DTD = 'aquaint-timebank.dtd';## Use the first one for those directories where the files only have# TimeML tags, use the second for those directories where the files # contain non-TimeML tags.## ========================================================================use strict;use XML::Checker::Parser;my $val = shift @ARGV;my $DIR;my $EXT = '';my $DTD = 'timeml_1.2.1.dtd';my $DTD = 'aquaint-timebank.dtd';    if ($val eq '-e') {    $EXT = shift @ARGV;        $DIR = shift @ARGV;} else {    $DIR = $val;}my $tmp_file = "tmp_validation_file.tml";opendir DIR , $DIR or die "Cannot open $DIR\n";my @files = sort grep /$EXT$/ , readdir DIR;open(STDERR, ">&STDOUT");foreach my $file (@files){    next if $file eq '.';    next if $file eq '..';    # Create temporay file so we can add the DOCTYPE line needed for    # DTD validation    open TML1,"$DIR/$file";    open TML2, "> $tmp_file" or die "Cannot write to $tmp_file\n";    print TML2 "<!DOCTYPE TimeML SYSTEM \"$DTD\">\n";    while (<TML1>) {        next if /^<\?xml version/;        print TML2;    }    close TML1;    close TML2;    print STDERR "\n\n==> $file\n\n";    my $parser = new XML::Checker::Parser ( Handlers => { } );    eval { $parser->parsefile($tmp_file); };    if ($@) {        print STDERR "\nPARSE FAILED\n";        print $@;    }}exec(`rm $tmp_file`);