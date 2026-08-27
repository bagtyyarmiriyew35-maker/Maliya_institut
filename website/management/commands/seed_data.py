import os
from django.core.management.base import BaseCommand
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from website.models import Page, SliderImage, News, Faculty, Department, Olympiad, Partner, Document

class Command(BaseCommand):
    help = 'Seeds mock data for the TDMai website'

    def handle(self, *args, **options):
        self.stdout.write('Seeding data...')
        
        # 1x1 Pixel transparent PNG as dummy image
        dummy_png = (
            b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06'
            b'\x00\x00\x00\x1f\x15c4\x00\x00\x00\rIDATx\x9cc`\x00\x00\x00\x02\x00\x01H\xaf'
            b'\xa4q\x00\x00\x00\x00IEND\xaeB`\x82'
        )
        slider_file = SimpleUploadedFile("slider.png", dummy_png, content_type="image/png")
        news_file = SimpleUploadedFile("news.png", dummy_png, content_type="image/png")
        faculty_file = SimpleUploadedFile("faculty.png", dummy_png, content_type="image/png")
        partner_file = SimpleUploadedFile("partner.png", dummy_png, content_type="image/png")
        doc_file = SimpleUploadedFile("doc.pdf", b"PDF dummy content", content_type="application/pdf")

        # Clear existing data
        Page.objects.all().delete()
        SliderImage.objects.all().delete()
        News.objects.all().delete()
        Faculty.objects.all().delete()
        Department.objects.all().delete()
        Olympiad.objects.all().delete()
        Partner.objects.all().delete()
        Document.objects.all().delete()

        # Seed Pages
        self.stdout.write('Seeding Page hierarchy...')
        
        # 1. Institut Parent
        inst_parent = Page.objects.create(
            title_tm="Institut", title_en="About the Institute", title_ru="Об институте",
            slug="institut",
            content_tm="Maliýe instituty barada maglumat.",
            content_en="Information about the Finance Institute.",
            content_ru="Информация о Финансовом институте.",
            order=1
        )
        Page.objects.create(
            parent=inst_parent,
            title_tm="Taryhy", title_en="History", title_ru="История",
            slug="taryhy",
            content_tm="Maliýe institutynyň taryhy barada giňişleýin maglumat...",
            content_en="Detailed history of the Finance Institute...",
            content_ru="Подробная история Финансового института...",
            order=1
        )
        Page.objects.create(
            parent=inst_parent,
            title_tm="Görkezijiler", title_en="Indicators", title_ru="Показатели",
            slug="gorkezijiler",
            content_tm="Institutymyzyň görkezijileri we üstünlikleri...",
            content_en="Indicators and achievements of our institute...",
            content_ru="Показатели и достижения нашего института...",
            order=2
        )
        Page.objects.create(
            parent=inst_parent,
            title_tm="Sanly bilim", title_en="Digital Education", title_ru="Цифровое образование",
            slug="sanly-bilim-page",
            content_tm="Sanly bilim ulgamy barada maglumat...",
            content_en="Information about the digital education system...",
            content_ru="Информация о системе цифрового образования...",
            order=3
        )
        Page.objects.create(
            parent=inst_parent,
            title_tm="Kitaphana", title_en="Library", title_ru="Библиотека",
            slug="kitaphana-page",
            content_tm="Maliýe institutynyň kitaphana hyzmatlary...",
            content_en="Library services of the Finance Institute...",
            content_ru="Библиотечные услуги Финансового института...",
            order=4
        )
        Page.objects.create(
            parent=inst_parent,
            title_tm="Wakansiýalar", title_en="Vacancies", title_ru="Вакансии",
            slug="wakansiyalar",
            content_tm="Institutymyzdaky boş iş orunlary we talaplar...",
            content_en="Available positions and requirements at our institute...",
            content_ru="Вакансии и требования в нашем институте...",
            order=5
        )

        # 2. Ylym Parent
        ylym_parent = Page.objects.create(
            title_tm="Ylym", title_en="Science", title_ru="Наука",
            slug="ylym",
            content_tm="Ylmy barlaglar we işler.",
            content_en="Scientific research and work.",
            content_ru="Научные исследования и работы.",
            order=2
        )
        Page.objects.create(
            parent=ylym_parent,
            title_tm="Ylmy-barlag işleri", title_en="Research Work", title_ru="Научно-исследовательские работы",
            slug="ylmy-barlag-isleri",
            content_tm="Maliýe institutynyň alyp barýan ylmy-barlag işleri...",
            content_en="Research work carried out by the Finance Institute...",
            content_ru="Научно-исследовательские работы, проводимые Финансовым институтом...",
            order=1
        )
        Page.objects.create(
            parent=ylym_parent,
            title_tm="Ýaş alymlar geňeşi", title_en="Young Scientists Council", title_ru="Совет молодых ученых",
            slug="yas-alymlar-genesi",
            content_tm="Ýaş alymlarymyzyň geňeşi we alyp barýan işleri...",
            content_en="Council of our young scientists and their work...",
            content_ru="Совет наших молодых ученых и их работа...",
            order=2
        )
        Page.objects.create(
            parent=ylym_parent,
            title_tm="Startap merkezi", title_en="Startup Center", title_ru="Стартап-центр",
            slug="startap-merkezi",
            content_tm="Maliýe institutynyň talyp startap taslamalary...",
            content_en="Student startup projects of the Finance Institute...",
            content_ru="Студенческие стартап-проекты Финансового института...",
            order=3
        )
        Page.objects.create(
            parent=ylym_parent,
            title_tm="Ylmy-barlag merkezi", title_en="Research Center", title_ru="Научно-исследовательский центр",
            slug="ylmy-barlag-merkezi",
            content_tm="Ylmy-barlag merkeziniň esasy ugurlary...",
            content_en="Main directions of the Research Center...",
            content_ru="Основные направления Научно-исследовательского центра...",
            order=4
        )
        Page.objects.create(
            parent=ylym_parent,
            title_tm="Ylmy gurnaklar", title_en="Science Circles", title_ru="Научные кружки",
            slug="ylmy-gurnaklar",
            content_tm="Talyplar üçin ylmy gurnaklar we durnukly bäsleşikler...",
            content_en="Scientific circles and regular competitions for students...",
            content_ru="Научные кружки и регулярные конкурсы для студентов...",
            order=5
        )
        Page.objects.create(
            parent=ylym_parent,
            title_tm="Ylmy-amaly maslahatlaryň tertibi", title_en="Conference Schedule", title_ru="График конференций",
            slug="maslahatlaryn-tertibi",
            content_tm="Maliýe institutynda geçiriljek maslahatlaryň meýilnamasy...",
            content_en="Schedule of conferences to be held at the Finance Institute...",
            content_ru="График проведения конференций в Финансовом институте...",
            order=6
        )

        # 3. Baslesikler Parent
        basl_parent = Page.objects.create(
            title_tm="Bäsleşikler", title_en="Competitions", title_ru="Конкурсы",
            slug="baslesikler",
            content_tm="Ykdysady we ylmy bäsleşikler.",
            content_en="Economic and scientific competitions.",
            content_ru="Экономические и научные конкурсы.",
            order=3
        )
        Page.objects.create(
            parent=basl_parent,
            title_tm="TDMaI bäsleşikleri", title_en="TDMai Competitions", title_ru="Конкурсы ТДМФИ",
            slug="tdmai-baslesikleri",
            content_tm="Institutymyz tarapyndan guralýan bäsleşikler...",
            content_en="Competitions organized by our institute...",
            content_ru="Конкурсы, организуемые нашим институтом...",
            order=1
        )
        Page.objects.create(
            parent=basl_parent,
            title_tm="Gaýry taraplar bäsleşikleri", title_en="External Competitions", title_ru="Внешние конкурсы",
            slug="gayry-taraplar-baslesikleri",
            content_tm="Beýleki guramalar we halkara guramalar tarapyndan geçirilýän bäsleşikler...",
            content_en="Competitions held by other organizations and international bodies...",
            content_ru="Конкурсы, проводимые другими организациями и международными органами...",
            order=2
        )

        # 4. Halkara Parent
        halkara_parent = Page.objects.create(
            title_tm="Halkara hyzmatdaşlyk", title_en="International Cooperation", title_ru="Международное сотрудничество",
            slug="halkara-hyzmatdaslyk",
            content_tm="Halkara hyzmatdaşlygy we gatnaşyklar.",
            content_en="International cooperation and relations.",
            content_ru="Международное сотрудничество и отношения.",
            order=4
        )
        Page.objects.create(
            parent=halkara_parent,
            title_tm="Halkara reýtingleri", title_en="International Ratings", title_ru="Международные рейтинги",
            slug="halkara-reytingleri",
            content_tm="Maliýe institutynyň halkara derejesindäki reýtingleri we üstünlikleri...",
            content_en="International ratings and achievements of the Finance Institute...",
            content_ru="Международные рейтинги и достижения Финансового института...",
            order=1
        )
        Page.objects.create(
            parent=halkara_parent,
            title_tm="Saparlar", title_en="Visits & Trips", title_ru="Визиты и поездки",
            slug="saparlar",
            content_tm="Daşary ýurtlara saparlar we halkara hyzmatdaşlar bilen duşuşyklar...",
            content_en="Visits abroad and meetings with international partners...",
            content_ru="Зарубежные визиты и встречи с международными партнерами...",
            order=2
        )
        Page.objects.create(
            parent=halkara_parent,
            title_tm="Okuwlar", title_en="Training Courses", title_ru="Обучение и тренинги",
            slug="okuwlar",
            content_tm="Halkara okuw maksatnamalary we seminarlar...",
            content_en="International training programs and seminars...",
            content_ru="Международные программы обучения и семинары...",
            order=3
        )
        Page.objects.create(
            parent=halkara_parent,
            title_tm="CirculEC", title_en="CirculEC Project", title_ru="Проект CirculEC",
            slug="circulec",
            content_tm="Durnukly ösüş we CirculEC taslamasynyň çäklerindäki işler...",
            content_en="Sustainable development and work within the CirculEC project...",
            content_ru="Устойчивое развитие и работа в рамках проекта CirculEC...",
            order=4
        )

        # 5. Dalasgar Parent
        dalas_parent = Page.objects.create(
            title_tm="Dalaşgär", title_en="Applicant", title_ru="Абитуриент",
            slug="dalasgar",
            content_tm="Dalaşgär talyplar üçin maglumatlar.",
            content_en="Information for prospective student applicants.",
            content_ru="Информация для абитуриентов.",
            order=5
        )
        Page.objects.create(
            parent=dalas_parent,
            title_tm="Bakalawr maksatnamasy", title_en="Bachelor Program", title_ru="Бакалавриат",
            slug="bakalawr-maksatnamasy",
            content_tm="Dalaşgärler üçin bakalawr hünärleri we okuw möhletleri...",
            content_en="Bachelor specialties and study durations for applicants...",
            content_ru="Специальности бакалавриата и сроки обучения для абитуриентов...",
            order=1
        )
        Page.objects.create(
            parent=dalas_parent,
            title_tm="Magistr maksatnamasy", title_en="Master Program", title_ru="Магистратура",
            slug="magistr-maksatnamasy",
            content_tm="Dalaşgärler üçin magistr hünärleri we okuw meýilnamalary...",
            content_en="Master specialties and study curricula for applicants...",
            content_ru="Специальности магистратуры и учебные программы для абитуриентов...",
            order=2
        )
        Page.objects.create(
            parent=dalas_parent,
            title_tm="Talyplyga dalaşgärler üçin ýeňillikler", title_en="Applicant Privileges", title_ru="Льготы для абитуриентов",
            slug="dala-yenillikler",
            content_tm="Olimpiada we ders bäsleşiklerinde orun alan dalaşgärler üçin göz öňünde tutulýan ýeňillikler...",
            content_en="Privileges for prospective applicants who won placements in Olympiads and competitions...",
            content_ru="Льготы для абитуриентов, занявших призовые места на олимпиадах и конкурсах...",
            order=3
        )
        Page.objects.create(
            parent=dalas_parent,
            title_tm="«Açyk gapylar» güni", title_en="Open Doors Day", title_ru="День открытых дверей",
            slug="acyk-gapylar",
            content_tm="Maliýe institutynda geçiriljek «Açyk gapylar» gününiň tertibi we wagtlary...",
            content_en="Schedule and timings of the 'Open Doors' days to be held at the Finance Institute...",
            content_ru="Расписание и время проведения Дней открытых дверей в Финансовом институте...",
            order=4
        )
        Page.objects.create(
            parent=dalas_parent,
            title_tm="Tanyşdyryş-mahabat", title_en="Introductory Promo", title_ru="Презентация и промо",
            slug="tanysdyrys-mahabat",
            content_tm="Maliýe institutynyň tanyşdyryş wideo rolikleri we mahabat bukletleri...",
            content_en="Introductory videos and promotional brochures of the Finance Institute...",
            content_ru="Презентационные видеоролики и рекламные буклеты Финансового института...",
            order=5
        )

        # 6. FAQ Page
        Page.objects.create(
            title_tm="Sorag-jogap", title_en="Sorag-jogap (FAQ)", title_ru="Вопросы и ответы (FAQ)",
            slug="faq",
            content_tm="Maliýe institutyna okuwa girmek we sapaklar barada ýygy soralýan soraglar...",
            content_en="Frequently asked questions about admissions and studies at the Finance Institute...",
            content_ru="Часто задаваемые вопросы о поступлении и обучении в Финансовом институте...",
            order=6
        )

        self.stdout.write('Seeded Page hierarchy completed.')

        # Seed Slider
        SliderImage.objects.create(
            image=slider_file,
            title_tm="Türkmen döwlet maliýe institutyna hoş geldiňiz!",
            title_en="Welcome to Turkmen State Finance Institute!",
            title_ru="Добро пожаловать в Туркменский государственный финансовый институт!",
            subtitle_tm="Bilim - bagtyýarlyk, ösüş we rowaçlyk.",
            subtitle_en="Education is happiness, development and prosperity.",
            subtitle_ru="Образование - это счастье, развитие и процветание.",
            order=1
        )
        self.stdout.write('Seeded SliderImage')

        # Seed Faculties and Departments
        faculties_data = [
            {
                "name_tm": "Bank işi", "name_en": "Banking", "name_ru": "Банковское дело",
                "dean_name_tm": "A. Meredow", "dean_name_en": "A. Meredov", "dean_name_ru": "А. Мередов",
                "description_tm": "Bank ulgamy üçin ýokary derejeli hünärmenleri taýýarlaýar.",
                "description_en": "Prepares high-level specialists for the banking system.",
                "description_ru": "Готовит высококлассных специалистов для банковской системы.",
                "departments": [
                    {"name_tm": "Bank işi", "name_en": "Banking", "name_ru": "Банковское дело", "head_name_tm": "B. Annajykow"},
                    {"name_tm": "Bedenterbiýe", "name_en": "Physical Education", "name_ru": "Физическое воспитание", "head_name_tm": "G. Garaýew"},
                    {"name_tm": "Ýokary matematika", "name_en": "Higher Mathematics", "name_ru": "Высшая математика", "head_name_tm": "M. Orazow"},
                ]
            },
            {
                "name_tm": "Hasap we audit", "name_en": "Accounting and Audit", "name_ru": "Учет и аудит",
                "dean_name_tm": "O. Saparowa", "dean_name_en": "O. Saparova", "dean_name_ru": "О. Сапарова",
                "description_tm": "Buhgalterçilik hasaba alnyşy we audit ugry boýunça hünärmenleri taýýarlaýan fakultet.",
                "description_en": "Faculty preparing specialists in accounting and auditing.",
                "description_ru": "Факультет, готовящий специалистов в области бухгалтерского учета и аудита.",
                "departments": [
                    {"name_tm": "Buhgalterçilik hasaba alnyşy", "name_en": "Accounting", "name_ru": "Бухгалтерский учет", "head_name_tm": "S. Geldiýew"},
                    {"name_tm": "Daşary ýurt dilleri", "name_en": "Foreign Languages", "name_ru": "Иностранные языки", "head_name_tm": "A. Amanowa"},
                ]
            },
            {
                "name_tm": "Maliýe", "name_en": "Finance", "name_ru": "Финансы",
                "dean_name_tm": "D. Durdyýew", "dean_name_en": "D. Durdyev", "dean_name_ru": "Д. Дурдыев",
                "description_tm": "Maliýe we ätiýaçlandyryş ugry boýunça hünärmenler taýýarlanýar.",
                "description_en": "Specialists in finance and insurance are trained.",
                "description_ru": "Готовятся специалисты в области финансов и страхования.",
                "departments": [
                    {"name_tm": "Maliýe", "name_en": "Finance", "name_ru": "Финансы", "head_name_tm": "K. Saryýew"},
                    {"name_tm": "Ätiýaçlandyryş işi", "name_en": "Insurance", "name_ru": "Страховое дело", "head_name_tm": "N. Nurmuradowyň"},
                    {"name_tm": "Maglumat tehnologiýalary", "name_en": "Information Technologies", "name_ru": "Информационные технологии", "head_name_tm": "E. Rejepow"},
                ]
            },
            {
                "name_tm": "Salgytlar we salgyt salmak", "name_en": "Taxes and Taxation", "name_ru": "Налоги и налогообложение",
                "dean_name_tm": "H. Aşyrow", "dean_name_en": "H. Ashyrov", "dean_name_ru": "Х. Аширов",
                "description_tm": "Salgyt ulgamy we ykdysadyýet nazaryýeti boýunça bilim berýän bilim ojagy.",
                "description_en": "Educational department providing training on tax systems and economic theory.",
                "description_ru": "Учебный центр, обучающий налоговой системе и экономической теории.",
                "departments": [
                    {"name_tm": "Salgytlar we salgyt salmak", "name_en": "Taxes and Taxation", "name_ru": "Налоги и налогообложение", "head_name_tm": "P. Nuryýew"},
                    {"name_tm": "Ykdysady nazaryýet", "name_en": "Economic Theory", "name_ru": "Экономическая теория", "head_name_tm": "J. Hydyrow"},
                    {"name_tm": "Jemgyýeti öwreniş ylymlary", "name_en": "Social Sciences", "name_ru": "Общественные науки", "head_name_tm": "O. Nobatow"},
                ]
            }
        ]

        for f_data in faculties_data:
            fac = Faculty.objects.create(
                name_tm=f_data["name_tm"], name_en=f_data["name_en"], name_ru=f_data["name_ru"],
                dean_name_tm=f_data["dean_name_tm"], dean_name_en=f_data["dean_name_en"], dean_name_ru=f_data["dean_name_ru"],
                description_tm=f_data["description_tm"], description_en=f_data["description_en"], description_ru=f_data["description_ru"],
                image=faculty_file
            )
            for dept_data in f_data["departments"]:
                Department.objects.create(
                    faculty=fac,
                    name_tm=dept_data["name_tm"], name_en=dept_data["name_en"], name_ru=dept_data["name_ru"],
                    head_name_tm=dept_data["head_name_tm"], head_name_en=dept_data.get("head_name_en", "Head"), head_name_ru=dept_data.get("head_name_ru", "Руководитель"),
                    description_tm=f"{dept_data['name_tm']} kafedrasy barada giňişleýin maglumat.",
                    description_en=f"Detailed information about the Department of {dept_data['name_en']}.",
                    description_ru=f"Подробная информация о кафедре '{dept_data['name_ru']}'."
                )
        self.stdout.write('Seeded Faculties and Departments')

        # Seed News
        news_data = [
            {
                "title_tm": "Niderlandlar Patyşalygynda geçiriljek ahalteke atlarynyň arasynda atly sport we gözellik bäsleşigi",
                "title_en": "World Akhal-Teke Horse Sports and Beauty Championship in the Netherlands",
                "title_ru": "Чемпионат мира по конному спорту и красоте ахалтекинских коней в Нидерландах",
                "content_tm": "Niderlandlar Patyşalygynda geçiriljek ahalteke atlarynyň arasynda atly sport we gözellik bäsleşiginiň dünýä çempionatyna biziň talyp we mugallymlarymyz gatnaşarlar.",
                "content_en": "Our students and teachers will participate in the World Akhal-Teke Horse Sports and Beauty Championship in the Netherlands.",
                "content_ru": "Наши студенты и преподаватели примут участие в чемпионате мира по конному спорту и красоте ахалтекинских коней в Нидерландах."
            },
            {
                "title_tm": "“MALIÝEÇI” GYZLAR WOLEÝBOL TOPARY — TÜRKMENISTANYŇ ÝOKARY LIGASYNYŇ ÇEMPIONY",
                "title_en": "'FINANCIER' WOMEN'S VOLLEYBALL TEAM — CHAMPIONS OF TURKMENISTAN HIGHER LEAGUE",
                "title_ru": "ЖЕНСКАЯ ВОЛЕЙБОЛЬНАЯ КОМАНДА «ФИНАНСИСТ» — ЧЕМПИОН ВЫСШЕЙ ЛИГИ ТУРКМЕНИСТАНА",
                "content_tm": "Institutyň 'Maliýeçi' gyzlar woleýbol topary uly üstünlik gazanyp, Türkmenistanyň ýokary ligasynyň çempiony boldular.",
                "content_en": "The institute's 'Financier' girls' volleyball team achieved great success and became champions of the higher league of Turkmenistan.",
                "content_ru": "Женская волейбольная команда института «Финансист» добилась больших успехов и стала чемпионом высшей лиги Туркменистана."
            },
            {
                "title_tm": "TÜRKMENISTANYŇ TALYPLAR WOLEÝBOL LIGASYNDA I ORUN",
                "title_en": "1ST PLACE IN THE VOLLEYBALL LEAGUE OF TURKMEN STUDENTS",
                "title_ru": "I МЕСТО В СТУДЕНЧЕСКОЙ ВОЛЕЙБОЛЬНОЙ ЛИГЕ ТУРКМЕНИСТАНА",
                "content_tm": "Biziň talyplarymyz woleýbol ligasynda birinji orny eýelediler we kubogy gazandylar.",
                "content_en": "Our students took first place in the volleyball league and won the cup.",
                "content_ru": "Наши студенты заняли первое место в волейбольной лиге и завоевали кубок."
            }
        ]

        for n in news_data:
            News.objects.create(
                title_tm=n["title_tm"], title_en=n["title_en"], title_ru=n["title_ru"],
                content_tm=n["content_tm"], content_en=n["content_en"], content_ru=n["content_ru"],
                image=news_file
            )
        self.stdout.write('Seeded News Items')

        # Seed Olympiads
        Olympiad.objects.create(
            title_tm="Informatika boýunça Döwlet Internet Olimpiadasy",
            title_en="State Internet Olympiad in Informatics",
            title_ru="Государственная интернет-олимпиада по информатике",
            year=2026,
            description_tm="Talyp ýaşlaryň arasynda informatika dersi boýunça internet bäsleşigi.",
            description_en="Internet competition in computer science among student youth.",
            description_ru="Интернет-олимпиада по информатике среди студенческой молодежи."
        )
        Olympiad.objects.create(
            title_tm="Buhgalterçilik hasaba alnyşy boýunça bäsleşik",
            title_en="Accounting Competition 2026",
            title_ru="Олимпиада по бухгалтерскому учету 2026",
            year=2026,
            description_tm="Maliýe instituty tarapyndan guralan hasapçylyk ders bäsleşigi.",
            description_en="Accounting competition organized by the Finance Institute.",
            description_ru="Конкурс по бухгалтерскому учету, организованный Финансовым институтом."
        )
        self.stdout.write('Seeded Olympiads')

        # Seed Partners
        Partner.objects.create(
            name_tm="Waýoming uniwersiteti (ABŞ)",
            name_en="University of Wyoming (USA)",
            name_ru="Вайомингский университет (США)",
            logo=partner_file,
            country_tm="Amerikanyň Birleşen Ştatlary",
            country_en="United States of America",
            country_ru="Соединенные Штаты Америки"
        )
        Partner.objects.create(
            name_tm="Azerbaýjanyň döwlet ykdysadyýet uniwersiteti (UNEC)",
            name_en="Azerbaijan State University of Economics (UNEC)",
            name_ru="Азербайджанский государственный экономический университет (UNEC)",
            logo=partner_file,
            country_tm="Azerbaýjan",
            country_en="Azerbaijan",
            country_ru="Азербайджан"
        )
        self.stdout.write('Seeded Partners')

        # Seed Documents
        reports = ["Aprel 10 - Aprel 17", "Aprel 03 - Aprel 10", "Mart 27 - Aprel 03"]
        for rep in reports:
            Document.objects.create(
                title_tm=f"Sanly hasabat - {rep}",
                title_en=f"Digital report - {rep}",
                title_ru=f"Цифровой отчет - {rep}",
                file=doc_file,
                category='Hasabat'
            )
        self.stdout.write('Seeded Documents')
        
        self.stdout.write(self.style.SUCCESS('Successfully seeded all data!'))
