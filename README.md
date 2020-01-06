# CoreNLG

## Contents :
- [General Information](#general-information)
- [Default text processing](#default-text-processing)
  - [Typographical conventions](#typographical-conventions)
  - [Automatic contractions](#automatic-contractions)
- [CoreNLG functions](#corenlg-functions)
  - [free_text](#free_text)
  - [nlg_syn and post_eval](#nlg_syn-and-post_eval)
  - [nlg_enum and nlg_iter](#nlg_enum-and-nlg_iter)
  - [nlg_num](#nlg_num)
  - [nlg_tags](#nlg_tags)
  - [no_interpret](#no_interpret)
- [CoreNLG classes](#corenlg-classes)
  - [Datas](#datas)
  - [Document](#document)
  - [Section](#section)
  - [TextClass](#textclass)
  - [TextVar](#textvar)
- [Quick start](#quick-start)

## General Information

CoreNLG is an easy to use and productivity oriented Python library for Natural Language Generation.\
It aims to provide the essential tools for developers to structure and write NLG projects.\
Auto-agreement tools based on extra-resources are <b>not provided</b> in this library.

## Default text processing

### Typographical conventions

You can chose a language (French or English) and typography will be automatically handled based on it.\
For example:\
In French 'Ma liste d'éléments:' becomes "Ma liste d'éléments :".\
In English "My list of items :" will become "My list of items:"

A period will always be followed by a capitalized word.

### Automatic contractions

Contractions are automatically handled based on the selected language (French or English).

```python
word_1 = 'le dépassement'
word_2 = 'les hausses'

self.free_text('À cause de', word_1) # "À cause du dépassement"
self.free_text('À cause de', word_2) # "À cause des hausses"
```

## CoreNLG functions

### free_text

The <b>free_text</b> method takes multiple strings or nested list/tuple of strings and return a string where each parameter is separated by a space. 
It aims to avoid forgetting the spaces between each element of a string when concatenating it.

```python
self.free_text(
  "The variation of the",
  indicator.label,
  "is",
  "positive" if indicator.variation > 0 else "negative" if indicator.variation < 0 else "not significant",
  "compared to last year."
)

self.free_text(
  "We can also use collection of strings as parameter,",
  (
    "if the next is true",
    "this text will be written"
  ) if test else (
    "else, we will",
    "have this text"
  ),
  "."
)
```

### nlg_syn and post_eval

The <b>nlg_syn</b> method takes multiples strings as parameters and return a string based on two modes.

```python
def synonym(self, *words, mode="smart")
```
  - "random": one of the strings in parameter will be chosen randomly.
  - "smart": the chosen string will be the best as possible considering previously chosen synonyms in order to avoid repetitions.

```python

# Basic use
self.free_text(
	
  'I was', 
  
  self.nlg_syn('hungry', 'starving'), 
  
  'so I decided to eat', 
  
  self.nlg_syn('one apple', 'three apples'), 
  
  '.'
	
)

# Synonyms trees can be made
self.free_text(
	
  'I was', 
  
  self.nlg_syn(
    'hungry so I decided to eat ' + self.nlg_syn('one apple', 'three apples'),
    'starving and I went to the restaurant'
  ),
  
  '.'

)
```

As you build complex structure, you will want to know at some point what word will be chosen to be able to match the rest of the sentence with it.\
Instead of a string, you can send a tuple as an argument to the <b>nlg_syn</b> method :
```python
self.nlg_syn(
  'one', 
  ('three', 'PLURAL')
)
```

You can now use the <b>post_eval</b> method which is defined as follow :
```python
def post_eval(
  key_to_check,
  string_to_write_if_active='',
  string_to_write_if_inactive='',
  deactivate_the_key=False
)
```

You can now build sentences like that :
```python
self.free_text(
	
  'I decided to eat',
  
  self.nlg_syn(
    'one', 
    ('three', 'PLURAL')
  ),
  
  self.post_eval('PLURAL', 'apples', 'apple', True),

  '.'  
)
# This will give you either "I decided to eat one apple." or "I decided to eat three apples."
# The 'PLURAL' key is now deactivated so next post_eval method would not find it.
```

### nlg_enum and nlg_iter

The <b>nlg_enum</b> method takes a list of element and an severatal arguments to create the output string. It returns a string.\

```python
def enum(self, my_list_of_elements,
               max_elem=None,
               nb_elem_bullet=None,
               begin_w=None,
               end_w=None,
               sep=None,
               last_sep=None,
               capitalize_bullets=None,
               text_if_empty_list=None,
               end_of_bullet=None,
               end_of_last_bullet=None)


class IterElems:
  def __init__(
    self,

    # maximum number of elements of the list that will be displayed
    max_elem=None, 

    # if the size of the list is superior to this number, it will create a bullet-point list
    nb_elem_bullet=None, 

    # the output string will begin with this string
    begin_w="", 

    # the output string will end with this string
    end_w="", 

    # separator for each element except the last
    sep=",", 

    # separator for the last item
    last_sep="and", 

    # each beginning of bullet-point should be capitalized
    capitalize_bullets=True, 

    # if the list is empty, this string will appear
    text_if_empty_list="", 

    # at the end of each bullet point except the last
    end_of_bullet = "", 

    # at the end of the last bullet-point
    end_of_last_bullet = "" 
  )
```


```python
my_list = ["six apples", "three bananas", "two peaches"]

self.nlg_enum(my_list)
# "six apples, three bananas and two peaches"

self.nlg_enum(my_list, last_sep="but also")
# "six apples, three bananas but also two peaches"


my_list = ['apples', 'bananas', 'peaches']

self.nlg_enum(
  my_list,
  max_elem=2, nb_elem_bullet=2, begin_w='Fruits I like :', end_w='Delicious, right ?', end_of_bullet=',', end_of_last_bullet='.'
)
"""
Fruits I like :
  - Apples,
  - Bananas.
Delicious, right ?
"""

my_list = ['apples', 'bananas']

self.nlg_enum([self.free_text(
  fruit,
  self.nlg_syn('so', '') + ' ' + self.nlg_syn('succulent', 'tasty')
) for fruit in my_list],
  begin_w='I find', end_w='.'
)
"""
One of the following:

I find apples so tasty and bananas succulent.
I find apples tasty and bananas so succulent.
I find apples so succulent and bananas tasty.
I find apples succulent and bananas so tasty.
"""
```

The <b>nlg_enum</b> method is a wrapper of <b>nlg_iter</b> which allows to do a bit more complex things.\
Instead of a list of elements, it takes a list of lists and strings. Through the iteration it maps every element with its associated ones. It then stops when there is no more elements in the smaller list.

```python
my_list_of_fruits = ['apples', 'bananas', 'peaches']
my_list_of_syno = [self.nlg_syn('succulent', 'tasty') for i in range(2)]

self.nlg_iter([
  my_list_of_fruits,
   "are",
   my_list_of_syno
])

# apples are tasty and bananas are succulent
```

### nlg_num

The <b>nlg_num</b> method allows to transform a number in a string following several criterion.

```python
def nlg_num(self, num, short="", sep=".", mile_sep=" ", dec=None, force_sign=False, remove_trailing_zeros=True)

my_number = 10000.66028

self.nlg_num(my_number, dec=3, force_sign=True) 

# +10 000.66
# The remove_trailing_zeros parameter will remove the last decimal even though we indicated 3 decimals because it is a 0.
```

### nlg_tags

The <b>nlg_tags</b> method allows to create HTML tags with attributes and encapsulate text into them.

```python
def nlg_tag(self, tag, text="", _class=None, **kwargs)

self.nlg_tags('br')
# <br>

self.nlg_tags('p', self.free_text(
  'This is a',
  self.nlg_tags('b', 'sentence with bold'),
  'in a paragraph.'
))
# <p>This is a <b>sentence with bold</p> in a paragraph.</p>


self.nlg_tags('div', 
  self.nlg_tags('h1', "My content"), 
  id="title_div"
) 
# <div id="title_div"><h1>My content</h1></div>
```

### no_interpret

The <b>no_interpret</b> method allows to deactivate the nlg interpretation (automatic contractions and typographical conventions) for a given string.

```python                         
# "This is a string.with a dot inside     ." becomes  "This is a string. With a dot inside." after NLG processing.

self.no_interpret("This is a string.with a dot inside     .")
# This is a string.with a dot inside     .
```

## CoreNLG classes

### Datas

The <b>Datas</b> class is used to store the input you receive.\
It should be inherited by your own custom data classes.

```python
class Datas:
  def __init__(self, json_in)

class MyDatas(Datas)
  def __init__(self, json_in)
     super().__init__(json_in)

my_datas = MyDatas(input)
```

### Document

The <b>Document</b> class is your final document wrapper.

```python  
class Document:
  def __init__(self, datas, title="", log_level="ERROR", css_path="css/styles.css", lang="fr", freeze=False)

my_datas = MyDatas(input)

document = Document(my_datas)
```

It takes at least an instance of a Datas class (or your custom one) as parameter.\
The 'freeze' parameter means that for every <b>nlg_syn</b> call, the chosen string will always be the first. It is useful for non-regression tests.

### Section

The <b>Section</b> class is a text zone of your document independant of others for the draw of synonyms.\
It is created from the Document class with the <b>new_section</b> method.\
You can give a HTML tag name in parameter (by_default 'div') and HTML attributes.

```python 
my_datas = MyDatas(input)

document = Document(my_datas)

first_paragraph_section = document.new_section(html_elem_attr={"id": "firstParagraph"})
second_paragraph_section = document.new_section(html_elem_attr={"id": "secondParagraph"})

document.write()
```

You should write your sections in the document with the <b>write</b> method of the class <b>Document</b>.\
You can also write each section separately to manage the order of the sections in the document with the <b>write_section</b> method.

```python 
def write_section(self, section, parent_elem=None, parent_id=None)
```

<b>You should not confuse a Section with a simple text zone.</b>

If you want your first and second paragraph to be independant, you create sections like we saw it above.\
If you just want to have two separates text zone in your document but without indepedancy on the synonyms, you create tags with <b>nlg_tags</b>.

```python 
paragraph_section = document.new_section()

paragraph_section.text = (
  paragraph_section.tools.add_tag('div', id='first_paragraph', text='First paragraph text'),
  paragraph_section.tools.add_tag('div', id='two_paragraph', text='Second paragraph text')
)
```

You will never use this way of calling the <b>nlg_tags</b> function because we created the <b>TextClass</b> object.

### TextClass

A <b>TextClass</b> is a class in which you will write your text. You should create your own sub-class for each part of your text.\
A TextClass takes a Section as parameter.

```python 
class MyDatas(Datas)
  def __init__(self, json_in)
     super().__init__(json_in)
     
     self.my_job = "developer"

class MyText(TextClass):
  def __init__(self, section):
    super().__init__(section)
    
    self.text = (
      "Hello",
      
      self.nlg_syn("world", "everyone"),
      
      ".", 
      
      self.nlg_tags('br'),

      self.nlg_tags('b', "Nice to meet you."),

      "I am a",

      self.my_job,

      "."
    )

my_datas = MyDatas(input)

document = Document(my_datas)

my_section = document.new_section(html_elem_attr={"id": "mySection"})

MyText(my_section)

document.write()

# <div id="mySection">Hello everyone.<br> <b>Nice to meet you.</b> I am a developer.</div>
```

The TextClass is a powerful object wich allows you to call all the [CoreNLG functions](#corenlg-functions) with self.\
You can also access every attributes of your Datas class the same way. 

The <b>self.text</b> write your text in the Section that was send as a parameter to your TextClass.\
You can use it with strings, nested lists or tuples and it will do the same job as the <b>free_text</b> function.\
Don't be afraid ! The '=' operator is override, to enjoy all the possibility of it, you should do :

```python
self.text = "Hello,"
self.text = "this is one sentence"
self.text = (
  "that I am",
  "writing here."
)

# Hello, this is one sentence that I am writing here.
```

### TextVar

The <b>TextVar</b> is a simple object, sub-class of str, whose '+=' operator is overloaded.\
It's the same principle as <b>free_text</b> and <b>self.text</b>, it works with strings and nested lists/tuples.\
It aims to ease the concatenation of strings.

```python
class MyText(TextClass):
  def __init__(self, section):
    super().__init__(section)
    
    self.text = self.nlg_tags('b', self.text_with_free_text())    
    self.text = self.nlg_tags('b', self.text_with_text_var()) 
 
  def text_with_free_text(self):
    return self.free_text(
      "first test is true" if test_1 else "first test is false",
      "and",
      (
	"second test",
        "is true"
      ) if test_2 else (
        "second test",
        "is false"
      )  
    )

  def text_with_text_var(self):
    my_text = TextVar()
    
    if test_1:
      my_text += "first test is true"
    else:
      my_text += "first test is false"
    
    my_text += "and"

    if test_2:
      my_text += "second test", "is true"
    else:
      my_text += (
        "second test",
        "is false"
      )

    return my_text		
```

In this example, the two methods returns equivalent strings. You can use both depending on which one you find the simpler to understand and the number of nested tests you have to write.

## Quick start

Install the library:

`pip install CoreNLG`

Create a basic template with cookiecutter:

```
pip install cookiecutter
cookiecutter https://github.com/societe-generale/core-nlg.git
```

You should obtain this architecture of project:

```
MyProject
|-- ProjectEntryPoint.py
|-- MyProject
|   |-- Datas
|   |   |-- MyDatas.py
|   |-- TextClass
|   |   |-- Introduction.py
|   |   |-- Content.py
|   |-- Resources
|   |-- Tools
|-- inputs
|   |-- test.json
```

ProjectEntryPoint.py will be your main, you can use it to test locally your application.

Run this file and you will see the HTML result in your console and your browser will render it automatically.\
Happy coding !
