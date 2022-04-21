from django.shortcuts import render, redirect
from .models import Collection
from django.contrib import messages
from .forms import RegisterForm, NewInput
from django.contrib.auth import login, authenticate, update_session_auth_hash, logout
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from parsimonious.grammar import Grammar
from parsimonious.nodes import NodeVisitor
from statistics import mode
from collections import Counter
import re

grammar = Grammar("""
	sentence = (digits/pn/nn/vb/adv/adj/prepo/articles/not_in_library/punctuations) space* sentence*
	digits = ~"[0-9]+"
	punctuations = ','/'.'/'!'/'?'
	space = ~"\s"
pn = 'is'/'in'/'it'/"me"/"myself"/"my"/"mine"/"yourself"/"yours"/"your"/"us"/"we "/"hers"/"she"/"they"/"us"/"her"/"him"/"themselves"/"ours"/"he "/"his"/"theirs"/"our"/"you"/"them "/"all "/"another"/"any"/"both"/"each"/"either"/"everybody"/"few"/"many"/"most"/"neither"/"nobody"/"no one"/"one"/"others"/"several"/"somebody"/"something"/"such"/"that"/"this"/"those"/"these"/"whatever"/"what"/"whoever"/"who"/"which"/"i"/'you'

nn = "today"/"birthday"/"tennessee"/"tokyo"/"store"/"python"/"city"/'month'/'morning'/'movie'/'movies'/'ability'/'access'/'accident'/'account'/'action'/'activity'/'act'/'addition'/'add'/'advantage'/'advice'/'affair'/'age'/'airport'/'air'/'alcohol'/'amount'/'analysis'/'animal'/'apple'/'art'/'average'/'back'/'balance'/'ball'/'bank'/'baseball'/'basket'/'basis'/'bathroom'/'bedroom'/'bed'/'beer'/'beginning'/'bird'/'blood'/'board'/'boat'/'body'/'bonus'/'bottom'/'boyfriend'/'brother'/'boy'/'building'/'cabinet'/'camera'/'cancer'/'candidate'/'capital'/'career'/'card'/'care'/'car'/'cash'/'category'/'cat'/'celebration'/'chance'/'chapter'/'charity'/'chemistry'/'chest'/'chicken'/'child'/'chocolate'/'choice'/'church'/'cigarette'/'class'/'client'/'climate'/'clothes'/'coast'/'coffee'/'college'/'combination'/'communication'/'community'/'computer'/'consequence'/'connection'/'context'/'course'/'country'/'county'/'credit'/'craft'/'cousin'/'culture'/'criticism'/'customer'/'dad'/'database'/'data'/'date'/'day'/'dealer'/'death'/'debt'/'decision'/'definition'/'delivery'/'demand'/'department'/'depression'/'depth'/'text'/'design'/'desk'/'development'/'device'/'diamond'/'difference'/'driver'/'dirt'/'dinner'/'dog'/'drama'/'an'/'downtown'/'party'/'there'/'home'/'presents'/'food'/'cake'/'snacks'/'snack'/'school'/'work'/'grade'/'time'/'games'/'game'/'place'/'beach'/'company'/'person'/'night'/'universe'

vb = "got"/"gone"/"go"/"run"/"travel"/"dance"/"came"/"flying"/"flew"/"fly"/"went"/"had"/"like"/"loved"/"am"/"live"/"are"/'why'/'want'/'was '/'has'/'favorite'/'break'/'laugh'/'play'/'sneeze'/'teach'/'create'/'eat'/'understand'/'learn'/'know'/'smell'/'am'/'were'/'does'/'do'/'did'/'will'/'can'/'would'/'might'/'get'/'brought'/'bring'/'needed'/'need'/'told'/'gave'/'found'/'made'/'said'/'heard'/'hear'/'won'/'love'/'decided'/'decide'/'lost'/'paid'/'allowed'/'allow'/'looked'/'look'/'called'/'call'/'tried'/'try'/'moved'/'move'/'hate'/'should'/'skip'/'skipped'

adj = "fat"/"beautiful"/"polite"/"big"/"happy"/"sad"/'adorable'/'aggressive'/'agreeable'/'alert'/'alive'/'angry'/'annoyed'/'anxious'/'arrogant'/'ashamed'/'attractive'/'average'/'awful'/'bad'/'better'/'black'/'yellow'/'orange'/'blue'/'purple'/'white'/'bored'/'blushing'/'blush'/'bright'/'busy'/'calm'/'clumsy'/'colorful'/'comfortable'/'confused'/'concerned'/'crazy'/'creepy'/'dangerous'/'dizzy'/'dull'/'fine'/'fantastic'/'frail'/'gifted'/'friendly'/'fair'/'elegant'/'healthy'/'helpless'/'helpful'/'hungry'/'hurt'/'jealous'/'lazy'/'long'/'obedient'/'perfect'/'poor'/'silly'/'sleep'/'rich'/'scary'/'strange'/'stupid'/'talented'/'tasty'/'witty'/'okay'/'exhausted'/'exhausting'

adv = "too"/"safely"/"always"/"even"/"exactly"/"far"/"fast"/"never"/"to"/"daily"/'often'/'seldom'/'regularly'/'yearly'/'weekly'/'yesterday '/'so'/'still'/'never'/'hourly'/'later'/'softly'/'madly'/'wildly'/'eagerly'/'bodly'/'finally'/'soon'/'last'

prepo = "off"/"on"/"addition to"/"except"/"until"/'about'/'as'/'at'/'after'/'against'/'below'/'between'/'but '/'by'/'down'/'following'/'for'/'from'/'minus'/'of'/'plus'/'regarding'/'than'/'since'/'up'/'without'/'with'/'over'/'upon'/'save'/'down'/'next to'

articles = 'an'/'a'/'the'

not_in_library = ~r"[-\w]+"
""")

grammar_exist = ["sentence","digits","punctuations","space","pn"
				,"nn","vb","adj","adv","prepo","articles","not_in_library"]

def containsNumber(value):
	if True in [char.isdigit() for char in value]:
		return True
	return False

# This is the longest code ever, I apologize for not having it more simplified but I didn't know how-to.
def data(response, id):
	ls = Collection.objects.get(id=id) # get one input from entire collection chosen
	text = ls.text # gets entire input
	words_ref = [] # every individual word, space and punctuation list
	# ----------------------------------
	# this tracks how many periods, commas, question, and exclamation marks found and arranges them to display and correlate
	# on the data page. For example, without these list. It will only show "Vb, NN, Pn", with this list it shows, "Vb - run", "NN - go"...
	track_per = []
	track_comm = []
	track_ques = []
	track_excl = []
	# ---------------------------------
	used_grammar = [] # used to find out which grammars were used in the input
	counts = [] # counts periods found to increment sentences

	fix = 0
	count = 0

	splits = text.split(" ") # splits input into list
	words_ref.append(text) # appending input into a words reference list 

	for i in range(len(splits)):
		words_ref.append(splits[i])

	# check if grammar will parse before continuing output
	try:
		grammar.parse(text.upper().lower())
	except:
		messages.error(response, "Something went wrong with your input. Please try something different.")
		redirect("main/home.html")

	text_parsed = grammar.parse(text.upper().lower())
	output = text_parsed
	text_parsed = str(text_parsed)

	# divide the tree to only get grammar used and words it found in quotation marks
	find_grammar = re.findall('"([^"]*)"', text_parsed)

	for i in range(len(find_grammar)):
		if find_grammar[i] in grammar_exist:
			if find_grammar[i] == grammar_exist[0] and find_grammar[i] in used_grammar:
				continue
			else:
				used_grammar.append(find_grammar[i])

	# find spaces and make sure to add them to their appropriate index found in the list
	for i in range(len(used_grammar)):
		if used_grammar[i] == "space":
			words_ref.insert(i, " ")
			if containsNumber(text) == True:
				if containsNumber(str(words_ref[i-1])) and i != len(words_ref):
					if "," in words_ref:
						words_ref.pop(i)
				if words_ref[len(words_ref)-1] == "!" or "?" or ".":
					if i+1 == len(words_ref):
						words_ref.pop(i)

	# if there are periods, count how many to justify for sentences amount
	for i in range(len(words_ref)):
		if "." in words_ref[i] and i != 0:
			if " " in words_ref[i-1]:
				count += 1
	#------------------------------------------------------------
	# This is where things get really complicated and long.
	# Only because I wanted to display the words found on the table, if I did not want that, then this would never be attached.
	for s in range(len(words_ref)):
		if s == 0: # continue because the first item in the list is just the complete input not broken up
			continue
		# If punctuations present, they need to be separated from the words
		# I was having this issue "I" "watched," "movie" in list instead of "I" "watched" "," "movie"
		# This fixes that, not that you'd ever put a comma between that
		if ("." or "," or "?" or "!" in words_ref[s]):
			string_name = str(words_ref[s])
			if string_name[-1] == ",":
				words_ref[s] = words_ref[s].replace(",", "")
				track_comm.append(s)
			if string_name[-1] == "?":
				words_ref[s] = words_ref[s].replace("?", "")
				track_ques.append(s)
			if string_name[-1] == ".":
				words_ref[s] = words_ref[s].replace(".", "")
				track_per.append(s)
			if string_name[-1] == "!":
				words_ref[s] = words_ref[s].replace("!", "")
				track_excl.append(s)

	# Where things get repetitive:
	# After removing the punctuations above with 'replace', I now need to add the punctuations
	# to the right position in the list so it counts when I show it in the table
	# For each comma, question mark, period, exclamation mark
	for i in track_comm:
		temp = words_ref[i]
		if count == 0:
			words_ref.insert(words_ref.index(temp)+1, ',')
			track_per = [i+1 for i in track_per]
			track_ques = [i+1 for i in track_ques]
			track_excl = [i+1 for i in track_excl]
		else:
			words_ref.insert(words_ref.index(temp)+2, ',')
			track_per = [i+1 for i in track_per]
			track_ques = [i+1 for i in track_ques]
			track_excl = [i+1 for i in track_excl]
		count +=1

	for i in track_ques:
		temp = words_ref[i]
		if count == 0:
			words_ref.insert(words_ref.index(temp)+1, '?')
		else:
			words_ref.insert(words_ref.index(temp)+2, '?')
		count +=1

	for i in track_per:
		temp = words_ref[i]
		if count == 0:
			words_ref.insert(words_ref.index(temp)+1, '.')
		else:
			words_ref.insert(words_ref.index(temp)+2, '.')
		count +=1

	for i in track_excl:
		temp = words_ref[i]
		if count == 0:
			words_ref.insert(words_ref.index(temp)+1, '!')
		else:
			words_ref.insert(words_ref.index(temp)+2, '!')
		count +=1
	# Complication ends
	#-----------------------------------------------------------------------

	# If comma, make sure to add a space after finding one
	for i in range(len(words_ref)):
		if words_ref[i] == ",":
			fix = i
		if i+1 == len(words_ref):
			if words_ref[fix] == ",":
				words_ref.insert(fix+1," ")

	# Append "sentence" to grammar found if there is more than one period
	for i in range(len(grammar_exist)):
		while s != 1:
			if count == 0:
				break
			used_grammar.append("sentence")
			count-=1
		counts.append(used_grammar.count(grammar_exist[i]))

	text_parsed = zip(used_grammar, words_ref)

	return render(response, "main/data.html", {"text_parsed":text_parsed, "text":text, "counts":counts, "output":output})

def all_stats(response):
	if not response.user.is_authenticated:
		messages.error(response, "You are not allowed to view this content. Please log in.")
		return redirect("/login")

	ls = response.user.collection.all() # get all of logged in user's collections
	text = []
	used_grammar = []
	counts = []
	count = 0

	for i in ls:
		text.append(i.text)

	text = ' '.join(map(str, text))
	splits = text.split()

	text_parsed = grammar.parse(text.upper().lower())
	output = text_parsed
	text_parsed = str(text_parsed)

	find_grammar = re.findall('"([^"]*)"', text_parsed)

	for i in range(len(find_grammar)):
		if find_grammar[i] in grammar_exist:
			if find_grammar[i] == grammar_exist[0] and find_grammar[i] in used_grammar:
				continue
			else:
				used_grammar.append(find_grammar[i])

	for i in range(len(splits)):
		if "." in splits[i] and i != 0:
			count += 1

	for i in range(len(grammar_exist)):
		while count != 1:
			if count == 0:
				break
			used_grammar.append("sentence")
			count-=1
		counts.append(used_grammar.count(grammar_exist[i]))

	most_occur = [word for word, word_count in Counter(splits).most_common(3)]

	return render(response, "main/alldata.html", {"text_parsed":used_grammar, "text":text, "counts":counts, "output":output, "most_used":most_occur})

def home(response):
	return render(response, "main/home.html", {})

def quickpost(response):
	if response.method == "POST":
			form = NewInput(response.POST)
			if form.is_valid():
				n = form.cleaned_data["text"]
				t = Collection(text=n)
				t.save()
			try:
				grammar.parse(t.text.upper().lower())
				return data(response, t.id)
			except Exception as e:
				messages.error(response, "This input contains strings not found in our dictionary, please try something different.")
				print(e)
				t.delete()
	else:
		form = NewInput()

	return render(response, "main/quickpost.html", {"form":form})

def collections(response, username):
	if response.user.is_authenticated:
		username = response.user.username
		ls = Collection.objects.all()
		if response.method == "POST":
			if response.POST.get("results"):
				return render(response, "main/data.html", {})
			if response.POST.get("create"):
				return redirect("/create")

		return render(response, "main/collections.html", {"ls":ls})
	else:
		return redirect("/login")

def delete_collection(response, id):
	collection = Collection.objects.get(id=id)
	collection.delete()
	return redirect("/collections/%s" % response.user.username)

def create(response):
	if response.user.is_authenticated:
		username = response.user.username
		if response.method == "POST":
			form = NewInput(response.POST)
			if form.is_valid():
				n = form.cleaned_data["text"]
				t = Collection(text=n)
				t.save()
				response.user.collection.add(t)
			try:
				grammar.parse(t.text.upper().lower())
				return redirect("/data/%i" % t.id)
			except:
				t.delete()
				messages.error(response, "This input contains strings not found in our dictionary, please try something different.")
		else:
			form = NewInput()
		return render(response, "main/create.html", {"form": form})
	else:
		return redirect("/login")

def register(response):
	if response.method == "POST":
		form = RegisterForm(response.POST)
		if form.is_valid():
			form.save()
			messages.success(response, 'Your account was successfully created!')
			return redirect("/login")
		else:
			messages.error(response, 'Please correct the error below.')
	else:
		form = RegisterForm()
	return render(response, "main/register.html", {"form": form})

def change_password(response):
	if response.user.is_authenticated:
		if response.method == 'POST':
			form = PasswordChangeForm(response.user, response.POST)
			if form.is_valid():
				user = form.save()
				update_session_auth_hash(response, user)  # Important!
				messages.success(response, 'Your password was successfully updated!')
				return redirect('change_password')
			else:
				messages.error(response, 'Please correct the error below.')
		else:
			form = PasswordChangeForm(response.user)
		return render(response, 'main/change_password.html', {'form': form})
	else:
		return redirect('/password_reset')

def logout_(response):
	logout(response)
	return render(response, 'registration/logout.html', {})
