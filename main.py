import pyjokes

def tell_joke(lang="en", category="all"):
    print(pyjokes.get_joke(language=lang,category=category))

if __name__ == "__main__":
    lang = input ("Choisissez une langue (en, de, es, it, gl, ) : ")
    joke_type = input ("Choisissez une categorie de blague (neutral, chuck, all ):")                                                                                 
    tell_joke(lang, joke_type)



