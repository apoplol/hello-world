#!/usr/bin/perl -T

use DBI;
use Digest::MD5 qw(md5_hex md5_base64);

$db="int420_171a23";
$user="int420_171a23";
$passwd="haZE3665";
$host="db-mysql.zenit";
$connectioninfo="dbi:mysql:$db;$host";

######Temporary bits of code and crap


#Pattern verification
my %PATTERNS = (
                "fname" => '[A-Z][a-z]{2,50}',
                "lname" => '[A-Z][A-Za-z]{2,60}',
                "login" => '[A-Za-z]{2,50}',
		"password" => '.{6,}',		
		"password2" => '.{6,}',
                "phone" => '^\d{3}-\d{3}-\d{4}$',
		"email" => '\w{1}[\w-.]*\@[\w-.]+',
		"addstreet" => '.{1,}',
		"addcity" => '[A-Z][a-z]{2,50}',
		"addprovince" => '[A-Z][a-z]{2,50}',
		"addcountry" => '[A-Z][a-z]{2,50}',
		"addpostal" => '^([A-Z][0-9]){3}$'
                );

#Holsd Form fields
my %FIELDS = (
		"fname" => "First Name",
		"lname" => "Last Name",
		"login" => "Login Name (must be unique)",
		"password" => "Password (min length 6)",
		"password2" => "Retype password",
		"phone" => "Phone number (###-###-####)",
		"email" => "Email",
		"addstreet" => "Street Address (## Street Name)",
		"addcity" => "City",
		"addprovince" => "Province",
		"addcountry" => "Country",
		"addpostal" => "Postal Code (A#A#A#)"
		);

#HTML HEADER
print "Content-type:text/html\n\n";

#FIRST TIME SCRIPT RUN
if ($ENV{'REQUEST_METHOD'} eq "GET")
	{
	&displayform();
	&showdb();
	exit;
	}

#PROCESS FORM, INSERT ENTRY
else
	{
	&parseform();
	&verifyform();
	&insertdb();
	exit;
	}

###################
####SUBROUTINES####
###################

sub displayform
	{
	print qq~
		<html>
		<head>
		<title>Black</title>
		</head>
		<body>
		<center>
		<form action="assignment.cgi" method=post>
		<h2>Registration Form</h2>

		Login: <input type=text name=login value="$form{login}"> $errors{login}<br>
		Password: <input type=password name=password value="$form{password}"> $errors{password}<br>
		Retype Password: <input type=password name=password2 value="$form{password2}"> $errors{password2}<br>
		First Name: <input type=text name=fname value="$form{fname}"> $errors{fname}<br>
		Last Name: <input type=text name=lname value="$form{lname}"> $errors{lname}<br>
		Phone Number: <input type=text name=phone value="$form{phone}"> $errors{phone}<br>
		E-mail: <input type=text name=email value="$form{email}"> $errors{email}<br>	
		<br><b><h4>ADDRESS</h4></b>
		Street Address: <input type=text name=addstreet value="$form{addstreet}"> $errors{addstreet}<br>
		City: <input type=text name=addcity value="$form{addcity}"> $errors{addcity}<br>
		Province: <input type=text name=addprovince value="$form{addprovince}"> $errors{addprovince}<br>
		Country: <input type=text name=addcountry value="$form{addcountry}"> $errors{addcountry}<br>
		Postal Code: <input type=text name=addpostal value="$form{addpostal}"> $errors{addpostal}<br>
		<br>
		<input type=submit value="Insert" name=Insert>
		<input type=reset value=Reset name=reset>
		</form>
		</body>
		</html>
		~;
	}

sub parseform

	{
	read STDIN,$qstring,$ENV{"CONTENT_LENGTH"};
	@pairs = split(/&/, $qstring);
	
	foreach (@pairs)
		{
		($key,$value) = split(/=/);
		$value =~ tr/+/ /;
		$value =~ s/%([a-fA-F0-9][a-fA-F0-9])/pack("C", hex($1))/eg;
		$form{$key} = $value;
		}
	}

sub verifyform
	{
	$missing = 0;
	#Test fields against regex
	foreach (keys %FIELDS)
		{
		if ($form{$_} !~ $PATTERNS{$_})
			{
			$errormsg="Data incorrect/missing in $FIELDS{$_}";
			$missing=1;
			} 
		else
			{
			$errormsg = "";
			}
		$errors{$_}=$errormsg;
		}

	#Test for duplicate username
	$select = qq~select login from ass1 where login = '$form{login}'~;
	$dbh=DBI->connect($connectioninfo,$user,$passwd);
	$sth=$dbh->prepare($select);
	$sth->execute();

	if(@row = $sth->fetchrow_array())
		{
		$errors{'login'} = "Name already registered";
		$missing = 1;
		}
	
	#Test for password twice
	if ($form{'password'} ne $form{password2})
		{
		$errors{'password2'} = "Passwords don't match";
		$missing = 1;
		}

	#Final failure check
	if ($missing == 1)
		{
		&displayform;
		&showdb;
		exit;
		}
	}

sub insertdb
	{
	#encrypt password
	$cryptpass = $form{password};
	my $salt = "Salt";
	$cryptpass2 = md5_hex($cryptpass . $salt);

	$insert = qq~insert ass1 (id, login, password, fname, lname, phone, email, addstreet, addcity, addprovince, addcountry, addpostal)
	values ('LAST_INSERT_ID()','$form{login}','$cryptpass2','$form{fname}', '$form{lname}','$form{phone}','$form{email}','$form{addstreet}','$form{addcity}','$form{addprovince}','$form{addcountry}','$form{addpostal}')~;
	
	$dbh=DBI->connect($connectioninfo,$user,$passwd);
	$sth=$dbh->prepare($insert);

	if($sth->execute())
		{
		&displaysuccess;
		&showdb;
		}
	else
		{
		&displayfail;
		&showdb;
		}
	$dbh->disconnect();
	}

sub displaysuccess
	{
	print qq~
		<html>
		<head>
		<title>Success</title>
		</head>
		<body>
		<h2>Record added</h2>
		</body>
		</html>
		~;
	}

sub displayfail
	{
	print qq~
		<html>
		<head>
		<title>Failure</title>
		</head>
		<body>
		<h2>Record failed</h2>
		</body>
		</html>
		~;
	}

sub showdb
	{
	print qq~<html>
		<head>
		<Title>Database</Title>
		</head>
		<body>
		<table border=1>
		<tr>
		<th>ID</th><th>Last Name</th><th>First Name</th><th>Phone Number</th><th>E-mail</th></tr>~;
	$select = qq~select id, lname, fname, phone, email from ass1~;
	$dbh=DBI->connect($connectioninfo,$user,$passwd);
	$sth=$dbh->prepare($select);
	$sth->execute();

	while(@row=$sth->fetchrow_array())
		{
		print qq~<tr>
			<td>$row[0]</td><td>$row[1]</td><td>$row[2]</td>
			<td>$row[3]</td><td>$row[4]</td>
			</tr>~;
		}
		
	print qq~</table>
		</body>
		</html>~;
	}
