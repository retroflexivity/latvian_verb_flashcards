# Flashcards for Latvian word forms

Learning Latvian word inflection might be hard for a foreigner. There are a lot of tools for learning languages, specifically flashcards like Anki or Memrise. However, if you want to learn word forms using a standard flashcard app, you need to add each form manually. This app changes this: a user only needs to add the infinitive form, and all other forms will be generated using [Tezaurs](tezaurs.lv) api.

Currently, only verbs are supported. Support for nouns etc. is a future task.

The target audience is beginner and intermediate leaners of Latvian who have struggle with learning word forms and look for a simple solution for it. In the app, a user can create decks of cards (words), and then study them. During a study session, the user sees a word in infinitive and need to inflect the word into a certain form. The app remembers which words the user guessed incorrectly and prioritizes them.

## Development plan
* ~~Basic login system~~
* ~~Database system, where users, decks, and cards are stored~~
* ~~Simple interface for deck and card addition~~
* ~~Wordform generation for verbs~~
* ~~Study screen and workflow, with session generation and answer submission~~
* ~~Default decks (currently one, for 1 conjugation verbs)~~
* Wordform generation for nouns etc.
* An interface to view and modify decks (delete cards, delete the deck)
* More default decks

## How to use the app
* Register in "Reģistrēties" window
* Default decks will be added to your account automatically automatically
* Add a deck: first "Jauna kārtiņu kolekcija" to create an empty deck. Then "Pievienot kārtiņu" to add a card: choose the required deck in the dropdown list
* Start a study session: click a deck name under "Mācīties".
  * 15 cards you have mastered the least will be selected and shuffled
  * You will be given a word and required features (e. g., tense (_laiks_), person (_persona_), and number (_skaitlis_). Write the required form into the text field and press _Pārbaudīt_ (e. g., for _darīt, Tagadne, 1, Vienskaitlis_ write _daru_).
  * If you answer correctly, a green notification will appear on top, the card will be removed from the session, and its mastery level will increase by 1. Otherwise, a red notification will appear, the card will be moved to the end of the session, and its mastery level will decrease by 2.
  * When all 15 cards have been answered correctly, the study session ends. You can repeat it with the new set of 15 least mastered cards or return to the home screen.

## The license
The MIT license is used for the app. This is a simple app that can be improved in many ways, and it is doubtful there will be any competition, so no copyleft license, like GNU GPL, is required. The MIT license is used because it is simple and very widely recognized.