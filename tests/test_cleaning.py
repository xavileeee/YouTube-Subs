from download_subs import clean_text, vtt_to_text


def test_clean_text_removes_brackets():
    s = "Hola [música] mundo"
    assert clean_text(s) == "Hola mundo"


def test_vtt_to_text_simple():
    vtt = """WEBVTT

00:00:00.000 --> 00:00:02.000
Hola

00:00:02.000 --> 00:00:04.000
Mundo
"""
    t = vtt_to_text(vtt)
    assert "Hola" in t and "Mundo" in t


def test_complex_vtt_cleanup():
    v = "Kind: captions Language: es Amigos,<00:00:02.320><c> sabéis</c><00:00:02.679><c> que</c><00:00:02.960><c> con</c><00:00:03.120><c> la</c><00:00:03.240><c> edad</c><00:00:03.639><c> uno</c><00:00:03.840><c> se</c> Amigos, sabéis que con la edad uno se Amigos, sabéis que con la edad uno se vuelve<00:00:04.279><c> cada</c><00:00:04.480><c> vez</c><00:00:04.759><c> menos</c><00:00:05.040><c> radical,</c><00:00:06.120><c> uno</c><00:00:06.399><c> tiene</c> vuelve cada vez menos radical, uno tiene vuelve cada vez menos radical, uno tiene más<00:00:07.080><c> en</c><00:00:07.240><c> cuenta</c><00:00:07.600><c> los</c><00:00:07.839><c> matices</c><00:00:08.280><c> de</c><00:00:08.440><c> las</c><00:00:08.639><c> cosas</c> más en cuenta los matices de las cosas más en cuenta los matices de las cosas <00:00:09.400><c> y</c><00:00:09.639><c> eso</c><00:00:09.840><c> de</c><00:00:10.080><c> hacerse</c><00:00:10.480><c> fuerte</c><00:00:10.840><c> en</c><00:00:11.040><c> algo</c> y eso de hacerse fuerte en algo y eso de hacerse fuerte en algo como<00:00:12.280><c> que</c><00:00:12.480><c> cada</c><00:00:12.719><c> vez</c><00:00:13.040><c> menos.</c><00:00:13.920><c> Sin</c><00:00:14.200><c> embargo,</c> como que cada vez menos. Sin embargo, como que cada vez menos. Sin embargo, una<00:00:15.240><c> de</c><00:00:15.400><c> las</c><00:00:15.639><c> pocas</c><00:00:16.039><c> cosas</c><00:00:16.440><c> que</c><00:00:17.000><c> uno</c><00:00:17.320><c> siente</c> una de las pocas cosas que uno siente una de las pocas cosas que uno siente una<00:00:18.160><c> sospecha</c><00:00:18.920><c> profunda</c><00:00:19.520><c> de</c><00:00:19.760><c> engaño</c><00:00:20.305><c> </c> una sospecha profunda de "
    raw = vtt_to_text(v)
    cleaned = clean_text(raw)
    assert '<' not in cleaned
    assert 'vuelve cada vez menos radical' in cleaned
    assert cleaned.count('vuelve cada vez menos radical') == 1
    # no double spaces
    assert '  ' not in cleaned


def test_clean_text_paragraphs_and_dedupe():
    raw = """Amigos, sabéis que con la edad uno se

Amigos, sabéis que con la edad uno se

Amigos, sabéis que con la edad uno se

vuelve cada vez menos radical, uno tiene

vuelve cada vez menos radical, uno tiene

vuelve cada vez menos radical, uno tiene

más en cuenta los matices de las cosas

más en cuenta los matices de las cosas

más en cuenta los matices de las cosas

y eso de hacerse fuerte en algo

y eso de hacerse fuerte en algo

y eso de hacerse fuerte en algo"""
    cleaned = clean_text(raw)
    # Each repeated group should only appear once
    assert cleaned.count('Amigos, sabéis que con la edad uno se') == 1
    assert cleaned.count('vuelve cada vez menos radical, uno tiene') == 1
    assert cleaned.count('más en cuenta los matices de las cosas') == 1
    assert cleaned.count('y eso de hacerse fuerte en algo') == 1
    # Should be grouped into 1 paragraph since there are no sentence terminators
    paragraphs = cleaned.split('\n\n')
    assert len(paragraphs) == 1


def test_clean_text_paragraph_joining_and_dedupe():
    raw = """migos, sabéis que con la edad uno se

Amigos, sabéis que con la edad uno se

Amigos, sabéis que con la edad uno se

vuelve cada vez menos radical, uno tiene

vuelve cada vez menos radical, uno tiene

vuelve cada vez menos radical, uno tiene

más en cuenta los matices de las cosas

más en cuenta los matices de las cosas

más en cuenta los matices de las cosas

y eso de hacerse fuerte en algo

y eso de hacerse fuerte en algo

y eso de hacerse fuerte en algo

como que cada vez menos.

Sin embargo,

como que cada vez menos.

Sin embargo,

como que cada vez menos.

Sin embargo,

una de las pocas cosas que uno siente

una sospecha profunda de engaño

es con el tema de la conquista espacial.

Son décadas observando tanta farsa,

tantos intentos de escenificar el

espacio con montones de contradicciones

y absurdos que desmontan las mismas

leyes de la física que tanto defiende,

que ahora quieren regresar a la

luna.

Bueno, tarde o temprano sabíamos

luna.
"""
    cleaned = clean_text(raw)
    paragraphs = cleaned.split('\n\n')
    # Ensure paragraph grouping and deduplication: the phrase should appear only once
    cleaned = clean_text(raw)
    assert cleaned.count('como que cada vez menos') == 1
    # The combined sentence 'Sin embargo, como que cada vez menos.' should appear
    assert any('Sin embargo, como que cada vez menos.' in p for p in cleaned.split('\n\n'))
    # Only one 'Sin embargo,' connector remains
    assert cleaned.count('Sin embargo,') == 1

    # A later paragraph should contain 'una sospecha profunda de engaño es con el tema de la conquista espacial.'
    assert any('una sospecha profunda de engaño es con el tema de la conquista espacial.' in p for p in paragraphs)
    # Last paragraph should end with 'sabíamos luna.'
    assert paragraphs[-1].endswith('sabíamos luna.')


def test_clean_text_strict_de_dupes_and_short_paras():
    raw = """Amigos, sabéis que con la edad uno se vuelve cada vez menos radical, uno tiene más en cuenta los matices de las cosas y eso de hacerse fuerte en algo como que cada vez menos. Sin embargo, una de las pocas cosas que uno siente una sospecha profunda de engaño

es con el tema de la conquista espacial.

Son décadas observando tanta farsa, tantos intentos de escenificar el espacio con montones de contradicciones y absurdos que desmontan las mismas leyes de la física que tanto defiende, que ahora quieren regresar a la luna. Bueno, tarde o temprano sabíamos que les vendría la fiebre otra vez y el momento ha llegado. Tomemos asiento porque el espectáculo está a punto de comenzar.

comenzar.

Se están aceptando reservas anticipadas y depósitos con cifras que van desde cientos de miles hasta millones de dólares. Imaginaos.

dólares. Imaginaos.

2030.

Rusia.
"""
    cleaned = clean_text(raw)
    # single-word or very short paras should be merged/eliminated
    assert all(p.strip().lower() != 'comenzar.' for p in cleaned.split('\n\n'))
    # duplicates collapsed
    assert cleaned.count('Imaginaos') == 1
    assert cleaned.count('2030') == 1
    assert cleaned.count('Rusia') == 1


def test_strict_paragraph_joining_example():
    raw = """Ahora vamos con el tercer caso y tú dijiste al inicio algo que me dejaste pensando. Entonces, vuelve a

repetirlo para que nos quede claro.

A ver, yo os comenté que el tercer caso era duro, era un caso muy sádico, muy incluso pornográfico. Es

cierto que este no se queda atrás, ¿eh?

esté está a la altura, diría que está a la altura del caso del monstruo este de

Cleveland, pero este es diferente. Es diferente porque puedes llegar a ver una cara del mundo sádico que incluso da miedo. Da miedo el decir, "Hostia, como a mí a mí a mí esto dio miedo.

Esto sí da miedo, pero esto es más un terror mental, terror mental, terror mental, ¿vale?

Es un terror mental. Este caso es similar porque también va a ocurrir en Estados Unidos, no va a ocurrir en 2002, va a ocurrir mucho tiempo antes, 1977, o sea, es mucho tiempo. Y voy a empezar la historia ubicándos también en una carretera. Resulta que hay una chica de 20 años, es una chica que se llama Colin Stan y es muy vividora. Esta chica,

¿qué te refieres que es muy vividora?

Muy vividora. Te lo explicaré después, pero primero quiero que entendáis que esta chica se encuentra en las carreteras de California haciendo autoestop porque quiere llegar a casa de una amiga, una amiga, una amiga,

¿vale? Esa amiga está de cumpleaños.

Ahora, ¿a qué me refiero con que Colín es muy vividora, me refiero que es una

chica que se mueve mucho por impulsos?"""
    cleaned = clean_text(raw)
    assert 'una amiga' in cleaned
    # repeated fragments like 'a mí a mí a mí' and 'terror mental, terror mental' should be collapsed
    assert 'a mí a mí a mí' not in cleaned
    assert 'terror mental, terror mental' not in cleaned


def test_merge_continuation_paragraphs():
    raw = """Amigos, sabéis que con la edad uno se vuelve cada vez menos radical, uno tiene más en cuenta los matices de las cosas y eso de hacerse fuerte en algo como que cada vez menos. Sin embargo, una de las pocas cosas que uno siente una sospecha profunda de engaño

es con el tema de la conquista espacial.
"""
    cleaned = clean_text(raw)
    # Should not split in two paragraphs, the second fragment is a continuation
    assert 'engaño es con el tema de la conquista espacial' in cleaned
    assert sum(1 for p in cleaned.split('\n\n') if 'conquista espacial' in p) == 1

