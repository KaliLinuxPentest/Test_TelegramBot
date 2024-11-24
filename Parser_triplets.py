import requests
from bs4 import BeautifulSoup
from rdflib import Graph, URIRef, Literal, Namespace, BNode
from rdflib.namespace import RDF, FOAF, DC, XSD, DCTERMS, SKOS
import re
from datetime import datetime

def create_base_graph():
    graph = Graph()
    
    # Добавляем стандартные пространства имён
    graph.bind('rdf', RDF)
    graph.bind('foaf', FOAF)
    graph.bind('dc', DC)
    graph.bind('dcterms', DCTERMS)
    graph.bind('xsd', XSD)
    graph.bind('skos', SKOS)
    
    # Создаем собственные пространства имён
    ART = Namespace('http://example.org/art/')
    PERSON = Namespace('http://example.org/person/')
    BIO = Namespace('http://example.org/bio/')
    KB = Namespace('http://example.org/kb/')
    MEDIA = Namespace('http://example.org/media/')
    
    graph.bind('art', ART)
    graph.bind('person', PERSON)
    graph.bind('bio', BIO)
    graph.bind('kb', KB)
    graph.bind('media', MEDIA)
    
    return graph, ART, PERSON, BIO, KB, MEDIA

def add_artwork_info(graph, ART, PERSON, BIO, MEDIA):
    # Мона Лиза и её альтернативные названия
    mona_lisa = ART.MonaLisa
    leonardo = PERSON.LeonardoDaVinci
    louvre = ART.Louvre
    
    # Основная информация о картине
    graph.add((mona_lisa, RDF.type, ART.Painting))
    graph.add((mona_lisa, DC.title, Literal("Мона Лиза")))
    graph.add((mona_lisa, SKOS.prefLabel, Literal("Мона Лиза")))
    graph.add((mona_lisa, SKOS.altLabel, Literal("Джоконда")))
    graph.add((mona_lisa, DC.creator, leonardo))
    graph.add((mona_lisa, DC.date, Literal("1503-1519")))
    graph.add((mona_lisa, ART.medium, Literal("масло, тополиная доска")))
    graph.add((mona_lisa, ART.dimensions, Literal("77 × 53 см")))
    graph.add((mona_lisa, DC.description, Literal("Знаменитый портрет работы Леонардо да Винчи, также известный как «Джоконда». Одна из самых известных картин в мире.")))
    graph.add((mona_lisa, ART.period, Literal("Высокое Возрождение")))
    graph.add((mona_lisa, ART.technique, Literal("сфумато")))
    graph.add((mona_lisa, ART.location, louvre))
    
    # Фильм о Леонардо
    leonardo_movie = MEDIA.LeonardoMovie2023
    graph.add((leonardo_movie, RDF.type, MEDIA.Movie))
    graph.add((leonardo_movie, DC.title, Literal("Leonardo")))
    graph.add((leonardo_movie, DC.date, Literal("2023")))
    graph.add((leonardo_movie, DC.description, Literal("Биографический фильм о жизни Леонардо да Винчи, рассказывающий о его становлении как художника и учёного")))
    graph.add((leonardo_movie, MEDIA.starring, Literal("Эйдан Тёрнер")))
    graph.add((leonardo_movie, MEDIA.director, Literal("Дэниэл Персивал")))
    graph.add((leonardo_movie, DC.subject, leonardo))
    
    # Информация о Лувре
    graph.add((louvre, RDF.type, ART.Museum))
    graph.add((louvre, DC.title, Literal("Лувр")))
    graph.add((louvre, ART.location, Literal("Париж, Франция")))
    graph.add((louvre, DC.description, Literal("Один из крупнейших и наиболее известных художественных музеев мира, расположенный в центре Парижа")))
    graph.add((louvre, ART.founded, Literal("1793")))
    
    # Информация о Леонардо
    graph.add((leonardo, RDF.type, FOAF.Person))
    graph.add((leonardo, FOAF.name, Literal("Леонардо да Винчи")))
    graph.add((leonardo, BIO.birthDate, Literal("1452-04-15")))
    graph.add((leonardo, BIO.deathDate, Literal("1519-05-02")))
    graph.add((leonardo, BIO.birthPlace, Literal("Анкиано, Флорентийская республика")))
    graph.add((leonardo, BIO.nationality, Literal("итальянский")))
    graph.add((leonardo, BIO.profession, Literal("художник, учёный, изобретатель")))
    graph.add((leonardo, DC.description, Literal("Великий итальянский художник и учёный эпохи Возрождения, один из самых известных полимеров в истории")))
    graph.add((leonardo, ART.notableWorks, mona_lisa))

def add_people_relations(graph, ART, PERSON, BIO, MEDIA):
    mona_lisa = ART.MonaLisa
    louvre = ART.Louvre
    leonardo_movie = MEDIA.LeonardoMovie2023
    
    # Информация о современных персонажах
    bob = PERSON.Bob
    alice = PERSON.Alice
    charlie = PERSON.Charlie
    
    # Боб - историк искусства
    graph.add((bob, RDF.type, FOAF.Person))
    graph.add((bob, FOAF.name, Literal("Боб")))
    graph.add((bob, BIO.birthDate, Literal("1990-01-15")))
    graph.add((bob, BIO.occupation, Literal("историк искусства")))
    graph.add((bob, BIO.education, Literal("PhD в истории искусств")))
    graph.add((bob, DC.description, Literal("Историк искусства, специализирующийся на эпохе Возрождения и творчестве Леонардо да Винчи")))
    graph.add((bob, FOAF.topic_interest, mona_lisa))
    graph.add((bob, ART.hasVisited, louvre))
    graph.add((bob, MEDIA.hasWatched, leonardo_movie))
    
    # Алиса - реставратор
    graph.add((alice, RDF.type, FOAF.Person))
    graph.add((alice, FOAF.name, Literal("Алиса")))
    graph.add((alice, BIO.birthDate, Literal("1992-03-20")))
    graph.add((alice, BIO.occupation, Literal("реставратор произведений искусства")))
    graph.add((alice, BIO.education, Literal("Магистр в области реставрации")))
    graph.add((alice, DC.description, Literal("Реставратор произведений искусства, специализируется на картинах эпохи Возрождения")))
    graph.add((alice, FOAF.topic_interest, mona_lisa))
    graph.add((alice, ART.hasVisited, louvre))
    graph.add((alice, MEDIA.hasWatched, leonardo_movie))
    
    # Чарли - музейный гид
    graph.add((charlie, RDF.type, FOAF.Person))
    graph.add((charlie, FOAF.name, Literal("Чарли")))
    graph.add((charlie, BIO.birthDate, Literal("1988-07-10")))
    graph.add((charlie, BIO.occupation, Literal("музейный гид")))
    graph.add((charlie, BIO.education, Literal("Бакалавр искусствоведения")))
    graph.add((charlie, DC.description, Literal("Профессиональный гид в музее, проводит экскурсии по залам с картинами эпохи Возрождения")))
    graph.add((charlie, FOAF.topic_interest, mona_lisa))
    graph.add((charlie, ART.hasVisited, louvre))
    
    # Отношения между людьми
    graph.add((bob, FOAF.knows, alice))
    graph.add((alice, FOAF.knows, bob))
    graph.add((alice, FOAF.knows, charlie))
    graph.add((bob, PERSON.collaboratesWith, charlie))
    graph.add((alice, PERSON.mentors, charlie))

def format_value(value):
    if isinstance(value, URIRef):
        uri_str = str(value)
        print(f"DEBUG: URI string = {uri_str}")  # Отладочная информация
        
        # Проверяем тип напрямую по URI
        if uri_str.endswith('Person') or 'Person' in uri_str:
            print(f"DEBUG: Detected Person type for {uri_str}")  # Отладочная информация
            return "Человек"
        elif uri_str.endswith('Movie') or 'Movie' in uri_str:
            print(f"DEBUG: Detected Movie type for {uri_str}")  # Отладочная информация
            return "Фильм"
        elif uri_str.endswith('Painting') or 'Painting' in uri_str:
            print(f"DEBUG: Detected Painting type for {uri_str}")  # Отладочная информация
            return "Картина"
        elif uri_str.endswith('Museum') or 'Museum' in uri_str:
            print(f"DEBUG: Detected Museum type for {uri_str}")  # Отладочная информация
            return "Музей"
        
        # Возвращаем последний компонент URI
        last_part = uri_str.split('/')[-1]
        print(f"DEBUG: Last part = {last_part}")  # Отладочная информация
        return last_part
    return str(value)

def format_predicate(predicate):
    if str(predicate) == str(RDF.type):
        return "22-rdf-syntax-ns#type"
    return str(predicate).split('/')[-1]

def create_chunks(triplets):
    chunks = []
    
    # Группируем триплеты по субъектам и типам
    subjects = {}
    types = {}
    for t in triplets:
        subject = t['субъект']
        if subject not in subjects:
            subjects[subject] = []
        subjects[subject].append(t)
        if t['предикат'] == '22-rdf-syntax-ns#type':  # Исправлено: тип -> 22-rdf-syntax-ns#type
            types[subject] = t['объект']
            print(f"DEBUG: Set type {t['объект']} for subject {subject}")  # Отладочная информация
    
    print(f"DEBUG: Found types: {types}")  # Отладочная информация
    
    def get_name(triplets):
        for t in triplets:
            if t['предикат'] in ['name', 'title']:
                return t['объект']
        return None
    
    def translate_name(name):
        """Переводит имена на русский язык"""
        translations = {
            'Alice': 'Алиса',
            'Bob': 'Боб',
            'Charlie': 'Чарли'
        }
        return translations.get(name, name)
    
    # Чанк для Моны Лизы (первый)
    for subject, triplets in subjects.items():
        if types.get(subject) == 'Картина':
            chunk = ["ПРОИЗВЕДЕНИЕ ИСКУССТВА"]
            chunk.append("-" * 40)
            chunk.append("НАЗВАНИЕ: Мона Лиза (Джоконда)")
            chunk.append("АВТОР: Леонардо да Винчи")
            chunk.append("ПЕРИОД СОЗДАНИЯ: 1503-1519")
            chunk.append("ИСТОРИЧЕСКАЯ ЭПОХА: Высокое Возрождение")
            chunk.append("ТЕХНИКА: сфумато")
            chunk.append("МАТЕРИАЛ: масло, тополиная доска")
            chunk.append("РАЗМЕРЫ: 77 × 53 см")
            chunk.append("МЕСТОНАХОЖДЕНИЕ: Лувр, Париж")
            chunk.append("ОПИСАНИЕ: Знаменитый портрет работы Леонардо да Винчи, также известный как «Джоконда». Одна из самых известных картин в мире.")
            chunks.append("\n".join(chunk))
            break
    
    # Чанк для Леонардо да Винчи (второй)
    for subject, triplets in subjects.items():
        if types.get(subject) == 'Человек' and any(t['предикат'] == 'name' and t['объект'] == 'Леонардо да Винчи' for t in triplets):
            chunk = ["ИСТОРИЧЕСКАЯ ЛИЧНОСТЬ"]
            chunk.append("-" * 40)
            chunk.append("ИМЯ: Леонардо да Винчи")
            chunk.append("ГОДЫ ЖИЗНИ: 1452-1519")
            chunk.append("МЕСТО РОЖДЕНИЯ: Анкиано, Флорентийская республика")
            chunk.append("НАЦИОНАЛЬНОСТЬ: итальянский")
            chunk.append("ПРОФЕССИЯ: художник, учёный, изобретатель")
            chunk.append("ОПИСАНИЕ: Великий итальянский художник и учёный эпохи Возрождения, один из самых известных полимеров в истории")
            chunks.append("\n".join(chunk))
            break
    
    # Чанк для фильма (третий)
    for subject, triplets in subjects.items():
        if types.get(subject) == 'Фильм':
            chunk = ["ФИЛЬМ О ЛЕОНАРДО ДА ВИНЧИ"]
            chunk.append("-" * 40)
            
            # Получаем данные о фильме из триплетов
            title = next((t['объект'] for t in triplets if t['предикат'] == 'title'), 'Leonardo')
            year = next((t['объект'] for t in triplets if t['предикат'] == 'date'), '2023')
            description = next((t['объект'] for t in triplets if t['предикат'] == 'description'), '')
            director = next((t['объект'] for t in triplets if t['предикат'] == 'director'), '')
            starring = next((t['объект'] for t in triplets if t['предикат'] == 'starring'), '')
            
            chunk.append(f"НАЗВАНИЕ: {title}")
            chunk.append(f"ГОД ВЫПУСКА: {year}")
            chunk.append(f"РЕЖИССЁР: {director}")
            chunk.append(f"В ГЛАВНОЙ РОЛИ: {starring}")
            chunk.append(f"ОПИСАНИЕ: {description}")
            
            # Добавляем информацию о зрителях
            viewers = []
            for person, person_triplets in subjects.items():
                if types.get(person) == 'Человек':
                    for t in person_triplets:
                        if t['предикат'] == 'hasWatched':
                            person_name = get_name(person_triplets)
                            if person_name:
                                viewers.append(person_name)
            
            if viewers:
                chunk.append("\nФИЛЬМ ПОСМОТРЕЛИ:")
                for viewer in sorted(viewers):
                    chunk.append(f"- {translate_name(viewer)}")
            
            chunks.append("\n".join(chunk))
            break
    
    # Чанк для Лувра (четвертый)
    for subject, triplets in subjects.items():
        if types.get(subject) == 'Музей':
            chunk = ["МУЗЕЙ"]
            chunk.append("-" * 40)
            chunk.append("НАЗВАНИЕ: Лувр")
            chunk.append("МЕСТОПОЛОЖЕНИЕ: Париж, Франция")
            chunk.append("ГОД ОСНОВАНИЯ: 1793")
            chunk.append("ОПИСАНИЕ: Один из крупнейших и наиболее известных художественных музеев мира, расположенный в центре Парижа")
            
            # Добавляем информацию о посетителях
            visitors = []
            for person, person_triplets in subjects.items():
                if types.get(person) == 'Человек':
                    for t in person_triplets:
                        if t['предикат'] == 'hasVisited':
                            person_name = get_name(person_triplets)
                            if person_name:
                                visitors.append(person_name)
            
            if visitors:
                chunk.append("\nПОСЕТИТЕЛИ МУЗЕЯ:")
                for visitor in sorted(visitors):
                    chunk.append(f"- {translate_name(visitor)}")
            
            chunks.append("\n".join(chunk))
            break
    
    # Чанки для современных персонажей (последние)
    for subject, triplets in subjects.items():
        if types.get(subject) == 'Человек' and any(t['предикат'] == 'name' and t['объект'] in ['Боб', 'Алиса', 'Чарли'] for t in triplets):
            person_name = get_name(triplets)
            if not person_name:
                continue
            
            chunk = ["СОВРЕМЕННЫЙ ПЕРСОНАЖ"]
            chunk.append("-" * 40)
            chunk.append(f"ИМЯ: {person_name}")
            chunk.append(f"ДАТА РОЖДЕНИЯ: {next((t['объект'] for t in triplets if t['предикат'] == 'birthDate'), '')}")
            chunk.append(f"ПРОФЕССИЯ: {next((t['объект'] for t in triplets if t['предикат'] == 'occupation'), '')}")
            chunk.append(f"ОБРАЗОВАНИЕ: {next((t['объект'] for t in triplets if t['предикат'] == 'education'), '')}")
            chunk.append(f"ОПИСАНИЕ: {next((t['объект'] for t in triplets if t['предикат'] == 'description'), '')}")
            
            # Интересы и активности
            interests = []
            for t in triplets:
                if t['предикат'] == 'topic_interest' and t['объект'] == 'MonaLisa':
                    interests.append("Интересуется картиной «Мона Лиза»")
                elif t['предикат'] == 'hasWatched':
                    interests.append("Смотрел(а) фильм «Leonardo»")
                elif t['предикат'] == 'hasVisited':
                    interests.append("Посещал(а) Лувр")
            
            if interests:
                chunk.append("\nИНТЕРЕСЫ И АКТИВНОСТИ:")
                chunk.extend(sorted(interests))
            
            # Отношения
            relations = []
            for t in triplets:
                if t['предикат'] == 'knows':
                    relations.append(f"Знаком(а) с {translate_name(t['объект'])}")
                elif t['предикат'] == 'collaboratesWith':
                    relations.append(f"Сотрудничает с {translate_name(t['объект'])}")
                elif t['предикат'] == 'mentors':
                    relations.append(f"Является наставником для {translate_name(t['объект'])}")
            
            if relations:
                chunk.append("\nОТНОШЕНИЯ:")
                chunk.extend(sorted(relations))
            
            chunks.append("\n".join(chunk))
    
    return chunks

def main():
    print("Создание расширенной базы знаний RDF...")
    
    # Создаем граф и получаем пространства имен
    graph, ART, PERSON, BIO, KB, MEDIA = create_base_graph()
    
    # Добавляем информацию
    add_artwork_info(graph, ART, PERSON, BIO, MEDIA)
    add_people_relations(graph, ART, PERSON, BIO, MEDIA)
    
    # Извлекаем и обрабатываем триплеты
    triplets = []
    for s, p, o in graph:
        subject = format_value(s)
        predicate = format_predicate(p)
        obj = format_value(o)
        
        description = {
            "субъект": subject,
            "предикат": predicate,
            "объект": obj,
            "контекст": predicate.capitalize()
        }
        
        triplets.append(description)
        print(f"DEBUG: Added triplet: {description}")  # Отладочная информация
    
    print(f"Всего создано {len(triplets)} триплетов")
    
    # Создаем чанки и сохраняем в файл
    chunks = create_chunks(triplets)
    print(f"DEBUG: Created {len(chunks)} chunks")  # Отладочная информация
    
    with open("rdf_triplets.txt", "w", encoding="utf-8") as f:
        f.write("БАЗА ЗНАНИЙ RDF\n")
        f.write(f"Дата создания: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 50 + "\n\n")
        f.write("\n\n###\n\n".join(chunks))
    
    print("DEBUG: File has been written")  # Отладочная информация

if __name__ == "__main__":
    main()
