# General notes

## 220620
Midagi on siin lahti selle serveriga, andori puhul lähevad aeg-ajalt topikud kuidagi risti. Teine probleem on slow start, ei saa kuidagi topikuid järjele. Peksad echo topikuid sisse, tagasi ei tule midagi. Parem oleks, kui see asi siiski töötaks libedamalt, muidu probleemid.  
Prooviks siis, et nummerdaks topikuid ja vaataks, millal kala sisse tuleb. Tundub, et ristiminek on sellest vast küll, et timeout on liiga väike ja siis mingid topicud jäävad nagu cachhi ja tulevad hiljem vastusena valedele küsimustele. No timeouti võiks ju suurendada, aga põhimõtteliselt ei ole üldiselt selge, mis oleks piisav. Indefinite wait koos mingi hästi suure timeoudiga? Phm võiks ju ka üldse indefinite waiti proovida, aga kas ta siis algselt ikka saabki midagi kätte? - No ei saagi.  
Nii me ei saagi aru, ilma slow stardi probleemi lahendamata, et mis seal edasi juhtub. Mingis mõttes see on ikkagi key. Üldiselt tundub, et kui saata üks topic välja ja oodata _mingi aeg_, siis järgmiste puhul läheb asi käima. - Jajah, seda kirjeldatakse kui _slow starter_ effekti, nii et üldiselt peaks võibolla tegemagii mingisuguse eraldi starter procedure mis ei käi läbi exchange. Või siis tegelikult hoopis mingi suht väikese timeoudiga pommitama seda, kuni sealt lõpuks vastus tuleb, see peaks dead aega vähendama.  
Muideks, ei saagi aru, et kas ta linuxi alt ühendades ei suuda initida või mis on (ot ei tegelikult peaks see ju ikkagi win alt töötama)
  
  No a siis peaks hakkama seda superprotseduuri vaatama, mis juhataks fittimist.  

## 220621
Well, mida me õieti peame tegema siin, on kätte saama spektri iDusest, siis selle ära fittima ja panema vst pildi tagasi, aga ma näen siin jälle seda probleemi, et tuleb midagi hakata muutma UI elementides. Teisest threadist. Siis peaks selle jaoks mingi signali defineerima ilmselt ja iduse VI peaks seda toetama. NoOk, seda ehk saame teha. Teine võimalus on kohalikku ui-sse teha paralleelne graafikaaken. Kolmas võimalus on tegelikult ka ikkagi derivetud VI-sse fittingu integreerimine, aga see nagu väga hea mõte vist ei tundu. Aga kuidas on üldine skeem näiteks alustamiseks vms? Esialgses oli selline skeem, et paned kaamerapildi jooksma, siis lülitad fittingu sisse ja välja ka, kui vaja. Üldiselt tundus see hea, aga kuidas seda siin teha. Et Kui panna scänning käima, siis läheb

## 220627
(nimetame selle pigem runninguks) läheb siis external moodi. Ja hakkab tsükliliselt pärima spektrit (ja x skaalat ka) ja fittima ning vastavaid tulemusi interpreteerima. Jseenesest võiks ju küll proovida, et Andori JY versiooni all on (võib-olla lükkame ka hiljem ülespoole) mingi slott, mis lisajoont graafikule tekitab. Võib-olla ruubiprocis võiks mingi history versioon olla perspektiivis, ano vaatame.  
Kuidagi see ajab nüüd ka ikka keeruliseks, et kas ei saaks näiteks timeriga teha, et otseselt UI elemente addressida, tegelikult timerit on vist ju nagunii vaja, sest kes muidu uuendab uid. Või noh ok, saab ka signaaliga ja võib-olla ongi loogilisem. Võimalikud

## 220628
Ruubiproc sai üldiselt käima ja käib ka isegi kaugmoel. Jooksvad mõtted, mis siin vaja teha veel oleks:
* ~~chkboxide changed ühendada~~
* r välja tuua (kuidas seda üldse leida?)
* fitijoone värvus
* ja hakata vaatama, mis juhul teda mõtet on  (vahemik?)
* siis edasi, et fitipiirkonda täpsustada (seda võiks isegi jooksvalt saada?)
* ja kas saaks kaks paralleelset teha?
* miks seal VI-s mõned asjad enabled-disabled vilguvad? (veider jah.)
* Andori tagasitoomise nupp ja ta võiks fitiaknaga koos ära kaduda.  

## 220707
Threadingu probleemid on ikka jube keerulised. Soovitatakse üldiselt pigem QThreadi kasutada, aga see eeldab threadi jaoks eraldi klassi moodustamist. Mis oleks võib-olla kasulik niikuinii, aga seal see andmete paigutus sel juhul oleks nigu on. Noh näiteks, kus siis sel juhul Andori... ei pagan, see võiks ikka olla main osas. No muidugi, sealsed signaalid võib ka threadiga ühendada, eriti threadist välja, aga siis peaks threadist saama ka jälgida, millal andmed tekivad. Üldiselt võiks threadi töö olla:
* Saadab välja stardi
* Ootab andmeid ja kinnitust, et eelmised andmed on töödeldud
* Saadab andmed edasi  

Üldiselt kaks viimast võivad aja kokkuhoiu mõttes olla ka vahetuses ja tegelikult pole tal vaja ka andmeid vahetada, vaid ainult teadet, et andmed on olemas, lugeda neid võib põhimõtteliselt ka põhiprogramm. Kuigi siis vist seal seda mingit andmete aegnihke trikki oleks keerulisem teha. (Milliseid andmemanipulatsioone oleks ergastuse puhul vaja teha?) Kule äkki prooviks esialgu siiski endise pythoni stiiliga, aga lihtsustatud threadiga asja käima saada, siis vaataks edasi.  
Häh. Tundub, et äkki siiski fittimise jätmine threadi polekski nii paha mõte, sest teatud tingimustel võib see võtta päris kaua aega (nõrga või puuduva signaali korral näiteks) ja  siis on kogu see aeg UI blokitud või vähemalt uimane. Iseenesest halb, eriti kui on palju interaktsiooni mingite UI elementidega (tahta näiteks 2 fitterit teha või mis iganes.) Kui õnnestuks kiiresti kindlaks teha, kas signaal on või pole, no siis isegi poleks hullu, olemasolevat signaali ta vast fitib mõistlikult

## 220831

Katsume asjasse nüüd jälle sisse elada. Mis siin probleem oligi? Kaks fitterit tahtsime teha. Ja häda oli, et mida panna threadi ja mida mitte. Võtsime fittimise sealt välja, aga siis selgus, et võiks jälle sisse tagasi panna. No kena. Probleem on seal põhiliselt andmete sisse-välja liigutamine, mida siis on rohkem. Aga katsub'akkama saada. Sest UI asju ei või threadis näppida. Tegime seda queueuedega.
Ühesng, et käsil oli Fitter objekti tekitamine, kuhu saaks anda ette funktsiooni, x ja y (vastavalt piiratud), andmete eelväärtused ja mis annaks välja tulemused, corr maatriksi või selle mingeid derivaate ja fititud funktsiooni. Kuidagi peaks olema ka inkorporeeritud mingi mehhanism, aru saamaks, kas fit on õnnestunud või mitte (millegi diskrimineeriv value võiks olla osa klassist).
Kuidas me händeldame slopitud backi? Võiks ju olla ka, et väljastpoolt (või ka seest) tehakse mingi summeerimise värk. Või mingi backgr, mis võib olla eri (ka 0) järku polünoom. Mingil moel võiks ju ka double see olla kokku liidetud; seal on eraldamise probleem, et kühmud kokku ei jookseks
Cyclicut peaks ka kuidagi arutama, kuidas teha. Arvestada tuleb, et väljast vaadates on 2 erinevat fittingut.
Tekkis selline idee, et fitfunc võiks saada olla mitme fn summa	see oleks mitmes mõttes hea, double kühmud ja backgroundid. kuidas seda teha, kas listina? s.m.e. x ja y vektor oleks sama, aga paramlistid liituks sest curve_fitile tuleb üle anda siiski üks konkreetne fn koos paramlistiga	ja kuidas täpselt käib algväärtustamine? Kaks võimalust, heuristiline ja tsükliline	aga viimane on võimalik ainult siis, kui sama fn-ga on juba midagi tehtud nii et keegi peab heuristika üle ka alati hoolt kandma. Aga kas seda saab teha klassi seest?	vist mitte, kuna see ei kavatse eriti konkreetsete funktsioonide tasemele laskuda.

No siis peab vist uurima, et kuidas listi pandud funktsioonidest üks summafunktsioon tekitada ja sellele paramlist üle anda? Prooviks võib võtta näiteks 2 lorentzit ja lin a+bx. Nii curve_fiti jaoks me peame tegema fn, mis võtab x vektori esimeseks parameetriks ja siis järjest mingi hulga parameetreid. No paistab, et selle saame. Kuskilt mingit testmaterjali ka oleks saada või? No üldiselt ka saime. Asi on enam/vähem, nüüd mõned juurutamise probleemid. Esiteks, kuidas toimub universaalne algväärtustamine.

## 220902 

Hei, nüüd on mingi Fitter object paika pandud, peaks talle mingi testi runnima. Võib-lla oleks seda kõige parem isegi teha Jupyterlabist, sest seal saaks ka (samust) pilti suht kergesti vaadata.

## 220906 

Jupyteris fitter naguvist e/v töötab, aga nüüd siis see thread võiks proovida paika ajada. Nüüd et kas eraldi klass või in-class worker on mõnevõrra küsimus, aga mis seal eraldi klassis küsimus on? Põhiliselt, et mingeid asju ei saa kätte nii lihtsalt, aga ilmselt saab alati kuidagi edasi ikka anda. Vaatame, mis vaja on: 
* startsignal (instrumendile alustada mõõtmist) (klassis olemas)
* stopevent (sulgeda thread) (klassis olemas) - selle tegelikult võiks lahendada ka nagu stoppablethreadis oli, et siseevent algul püsti, aga on olemas stop() funktsioon
* data sisse queue - mul on siin küsimus, et kuidas x data sisse anda? Seda küsiti muidu threadis otse instrumendilt, aga see väga normaalne ei tundunud. Kuna see võib muutuda, siis peaks seda iga kord ikka lugema
* tulemus välja, ilmselt signal (define klassis või välisklassis)
* parameetrid sisse queue (ega sellega ka tegelikult oleks loogiline eraldi prots teha)

Kuna need on kõik threadsafe asjad, siis tegelikult nende accessimine klassi sees ei tohiks iseenesest olla probleemiks

## 220908

Ok nüüd vaatame, kuidas saaks selle põhiprogrammiga ühendatud meie uue threadi. Küsimusi tekitab siin see, et kuidas mitme (2) hvitteri widgetid kõik parimini ühendada. 

## 220909

Nii, sai nüüd masina peal veidi katsetama hakatud ja mingi hulk kolle ka välja, aga midagi on veel siin selgitada:

* mingil hetkel, kui ma ei tea millise mudeli vahetuse juures tuleb, et fitter.py", line 33, in fitfn
    result += f(x, *args[offset:offset + self.parno[i]]) TypeError: linear() missing 1 required positional argument: 'B'. Ja seda fitfn-i kutsutakse curve_fitist.
    * See on vist näiteks siis ka, kui sloped välja lülitada, ehk siis et toimub parameetrite vähendamine...
    * Asi selles, et see paramlist on algul list, aga pärast curve_fitist läbi käimist muutub numpy arrayks. Ilmselt peaks ta siis algusest peale arrayks tegema äkki või kumbapidi? Võib ka listiks teda proovida jätta.
* Siis oli veel nii ka, et kui ühel pool mudel näiteks single lorentzi peale viia, siis teisel pool on double lorentz ja selle näit muutub mingiks negatiivseks (teine kühm?)`
* Nüüd cyclicu osas peab veel midagi mõtlema, sest kui ta praegu käest ära läheb, siis cyclicu väljavõtmine vist ei aita (kuigi võib aidata mudeli vahetus). Ma ei tea, kas mudeli vahetust peaks proovima nii teha, et ei uuendata mõlemat korraga.
* Ma ei tea, kuidas limbi järgi saaks Jobinis skaalauuendust tegema hakata, kas seal neoonijoonte dialoogis võ?
* Miks uncertlistis midagi ei tule? - ei ikka tuleb, aga väike oli lihtsalt
* ikkagi see Andori pildis mingid asjad seal vilguvad? Runni ajal.
* spektromeetri nupp proc dialoogis.
* Kas runni lõppedes peaks overlayd ära koristama? Või ka fitteri desaktiveerimisel?

## 220920

Vaata eelmised üle ja:

* poolpiksli võimalus lambdas
* set0 nupud ühendada
* diskrimineerimine ja init!


## 221013 

Siin küsimusi on tekkinud nüüd Chira peal exciti tegemisega. Ja mõned nendest on:

* salvestamise workflow, mis väärib vist pikemat diskussiooni
* siis miks ergastuse esimene punkt kipub alati tulema väga suur (guess on, et getPWR annab millegipärast 1.0?)
* Noh üldine suurem teema on veel masinate sisse-väljalülitatus ja selle arvestamine
* Räägiti ka, et shutter lahti kinni nupp pole hästi nähtav, no see on win 11 peal veel hullem

Salvestamine siis. Kuidagi peaks olema välditud ülekirjutamine. Siis, see ... Nimede genereerimine võiks kuidagi toimuda. Võib-olla võiks ka zip kirjutamise peale mõelda. Eniway, see võiks olla ka ikka mingis baasklassis lahendatud. Aga mõtleme. Kõigepealt, kuidas baasklass paika saada. 
No holetame, et baasklassiks tuleb see My Docus ja seda võib edasi panna (võib ka automaatselt nt. kuupäeva foldri teha, kuigi tegelikult on seal järgmine tase ju üldiselt tegija nimi.) Nii, siis võiks seal olla võimalus, et hakatakse tegema kas nummerdatud või kellaajalisi foldereid ja siis sinna alla kas kaks foldrit või kaks zippi. ainult nummerdust on veits keeruline üldjuhul teha (või noh, mista ka niiväga), aga kellaajalised on veidi arusaamatud. Peaks ka vaatama, et üldiselt oleks seal näiteks scan.txt või midagi olemas, siis ta teeb jooksvat salvestamist ka.


## 221018

* pikad import nimed, kas nendega midagi ei saa teha?
* vinsti baasklass on juba lausa karjuv, kuidas lahendada instr/adapter ja siis protseduuri klass (kus on save, aga instrumentide asemel on teised vinstid ja externaliga on ka teised lood)
* Võib-olla üldisema timer / thread lähenemise peale peaks ka mõtlema

Muide mingi väga keeruline on tekitada mingit mõistlikku installivarianti nii, et mitte-py failid ka arvesse võetaks. https://stackoverflow.com/questions/24347450/how-do-you-add-additional-files-to-a-wheel - Siin on hulgaliselt variante, mis ühel töötasid, teisel mitte, ei hakanud neid isegi mitte proovima. Tekitab praegu whl-i (python setup.py bdist_wheel) ja pipinstallib selle, siis ülejäänud failid (dll,ui,ico,conf) vaatab käsitsi, et nad paigal on.

## 221108

Nüüd siis Ruby_Proc juures tagasi ja ka Stage figureerib siin, nimelt et kas on mõtet teha mingit scänni koos sellega, et võimaldaks hulga keri läbi käia. Võib-olla on, aga siis, et kuidas ja mida salvestada? 

Vahelduseks, et vahepeal sai tehtud Chirale protseduur koos Flamega, aga pole väga kindel, et see on perspektiivne, nimelt mis selgub on, et (seda sai vaadata Kymeraga tegelikult) punases on selline pilt, et Xe jooned tungivad sisse, ergastus on hulga laiem kui pilu ette näeb ja joonte korral mitme maksimumiga, mis üldjuhul ei lange kokku ettenähtud lainepikkusega. Muus piirkonnas on pilt igatahes parem; võib-olla väikeseks korrektsiooniks võiks teoreetiliselt mingi referents olla, aga võib-olla see pole ka nii oluline. Niisiis, et kuni ca 700 nm-ni on olukord päris hea, sealt 800-ni teatud mööndustega, aga siis edasi juba pole Chira selliseks otstarbeks väga kasutatav. Võib-olla teatavat võimsusreferentsi isegi võib saada, kui nt läbivalgustusrežiimi kasutada, aga lainepikkusskaalat eriti usaldada ei tasu. Seega tuleks siis Ti-Sph töölepaneku peale tõsisemalt mõelda jällegi.

Ok, aga tagasi Jobin-Yvoni juurde. Oot ma nüüd ei saa aru: Sai MCL stage-le tehtud just positsioonide seivimise võimalus ja nüüd ma avastan, et teisel päeval on kõik positsioonid kuidagi nihkes. Ei tundu, et oleks nihkunud rakk, kus need kerad sees on, siis kas on paigast läinud enkooder kuidagi? Sel juhul tuleb mingi offset kasutusele võtta, mida iga kord uuesti määrata? Programmi uuestikäivitamisel igatahes tundub koht säilivat. Proovime siis kasti välja-sisse lülitada. - See ka justkui ei mõjutaks eriti? Kuidagi pikema aja jooksul siis? Seda kiiresti proovida ei saa. 

Üritan saada mingit tunnetust, et kuidas nende keradega peaks õieti käituma, sest tundub, et erinev positsioneering kerale annab kuigivõrd ikka erineva rõhu küll. Määramatusehinnangut peaks ka tegema, aga tundub, et see siiski on midagi veel lisaks sellele. 

Tegin siis mingi rõhutsükli ära, algväärtused on küll üsna erinevad. Vaatasin 4 kera, üks oli nn. nullkera. Üldiselt on mulje, et rõhukonstandid on üpris samad (määramatuse piires), aga üks väiksem kera, sellel tundus, et oleks nagu veidi väiksem olnud see koef. Aga kuidas mingi korralikum katse teha, seda peab õieti mõtlema, siin on oluliseks faktoriks veel ka aeg. Rõhu muutmise järel relakseerumine toimub ikka üpris pikalt, nagu siin näha oli, kiirem osa paari minutiga, aeglasem kasv jätkub veel paarkümmend minutitki. 

Lasin lõpuks välisrõhu 1 bar peale, sellest sees rõhk kohe ei muutunud kuigi palju (6.4 -> 5.7 kbar), aga küllap ta vaikselt langeb. Näis, mis üleöö teeb.

## 221216 

Kus ma siia kirja paneks, et mis refaktoorimist oleks vaja mingil hetkel teha:

* stringi formatt % pealt .format'i peale
* instrumentides parem valmidus erroonilisteks tulemusteks (siin-seal midagi ka on)
* ja ühtlasi siis ka ühendatuse - ühendamise (ja vastupidi) kontseptsioon. Võib-olla võiks see olla viidud ka baasinstrumenti.

## 221220

Proovin siin sotti saada igasugu määramatusarvutustest ja nende progresseerumisest. Neooni joonte paigalefittimine on praegu siin teema ja kui ma saan sellised tulemused:

692.94675 392.733 0.014 

693.7664  506.920 0.063 

696.5431  895.426 0.014 

ja kattetegur 99% jaoks on 2.78 siin koguaeg, siis mida siit järeldada saab? Vaatan praegu, et siin äkki tuleks isegi mõlemat pidi mingit määramatust arvestada, kui juba nii, sest ma ei tea, kui täpselt ka neid Ne andmeid kuskilt leida saab; samm on ju 0.00715 näiteks ja kui me isegi loeme kõik numbrid täpseks, siis lainepikkuste abs. määramatus on ikka väiksem kohati.

## 230103 

Jäin praegu mõtlema selle peale, et kuidas liitinstrumendid üle võrgu töötavad ja sealjuures kuidas ühendada nad sama VInstrumendi külge. Seal on kaks võimalust, et kas ühendamine toimetada instrumendi või VI tasemel. Viimane oleks eelistatum, kui ühinemine toimub üle eri adapterite (põhimõtteliselt poleks vast võimatu ka mitme adapteri kasutamine instrumendis, mis siis tuleks mõlemad ette anda, aga kui nüüd edasi mõelda ZMQ vms. peale, siis seal tuleks ju ka anda kaks vastavat adapterit ja olukord poleks selles mõttes kuigi erinev.) 

Ok, probleem ühesõnaga tekib sellest, et kui meil on mitu instrumenti ja me peaksime igaühele neist tekitama eraldi nt. ZMQAdapteri, siis oleks neile vaja ka võimalust eraldi ette anda aadress, inport ja outport, sest isegi kui me eeldame, et seadmed on ühendatud sama masina taha, siis mitu adapterit ei saa saata samasse porti, s.o. minimaalselt on meil vaja erinevaid outporte. Oot kummal pool oli aadress? Kuulaja vist - jah, sub'i pool. Ehk siis, et aadress ja inport on kuulamiseks ja need võivad mitmel adapteril ka samad olla, aga outport on erinev. Kuigi inpordiga on ka see küsimus, et ah ei tegelikult vist ei ole ka, server vist ei pea mitut porti avama, saadab info vastava märgendiga kõik ühte porti, kui meil just mitut serverit samas masinas käimas pole, mis on vist ka võimalik (arvestades, et server peab kohaliku adaptri siiski avama ja seega masin peab valmis olema, isegi kui teda ei tarvitata, aga seda võib ka settingutega reguleerida, kuigi alternatiiv on ka mitu serverit). Iseasi muidugi, kui me kuidagi ajaksime nad sama adaptri peale, sellega küll piirates võimalust, et seadmed mitmes masinas olla saaksid, aga siis peaks kuidagi saama võimalikuks infot eri märgenditega saata, mis vist oli meil ka adaptri osa. Kuigi reaalselt praegu väga näha ei ole liitseadmeid, mille osad oleks eri masinate küljes, aga üldjuhul ei saa ju seda ka välistada. 

Formaalselt praegu vist ei ole probleemi lokaalse adapteri korral süsteemi tööle saada ka mitu korda getAdaptrit kutsudes (õieti, mis tast kutsuda, kui ta ikka sama adaptri tagasi annab), aga sisuline probleem on täitsa olemas. Ti-sph jaoks näiteks, kui mitte muidu, ja seal võib lisaks vaja olla ka Jobin-Yvonni samal ajal käitada. Aga kas siis ei saakski lihtsalt kõik need pordid jm. getAdaptrile anda? Õige, aga kusagilt peab saama nad ju algkäivitada ka ja võib-olla selle üldsettingute formaadi üle peakski mõtlema. Näiteks, et selle saadetud refname põhjal üritatakse kuskilt (nt. instrumendiga samast kohast) midagi lugeda ja kui pole, siis proovitakse kohalikku. Või noh, võib ka mingeid masinapõhiseid kohti välja mõelda, arvestades, et samas masinas üldiselt püsib olukord küllaltki sama, aga VInst all olev info läheb syncimisele. Seal võiks ju siis ka muidki settinguid säilitada. No näe, mõtteid tuleb.

## 230104

No nüüd sai hakatud seda implementeerima, et kuidas ZMQ võimalikku ühendust kontrollida ja praegu on nii, et igal seadmel on mingi refname ja selle kohta on masina seadetes (AppData/Local või ~/.config) all laborIott/Inst/< refname >.ini, kui on vaja seda saada üle võrgu või muid seadeid salvestada. Selles peab siis olema [ ZMQ ] sektsioon ja seal address, inport, outport, active ja address on ainuke kohustuslik. Mingeid segadusi siin ka kohe ilmnes. Sama seadet võib tahta nii lokaalselt kui üle võrgu ja sel juhul peaks olema võimalik neile eri refnamed anda. Seda siis ka sai korraldatud, refname(d) mingi defauldiga võiksid siis olla VI parameetrites ja tegelikult võiks neid ka promoveerida command linele. Siis instrumendi tasemel liidetud instrumendid (kui on vaja mitte juurde deffida instrumenti, vaid asendada), nt. Kymera, sai instrumendi defineerimine eraldi funktsiooni tõstetud, siis on võimalik seda overrideda.

##  230105

Kena, aga üks kaalutlus veel lisandus. Asi selles, et getAdapter võtab kohe ette default adapteri, koostades juba kohe ära ka vastava adapteri objekti. Selgub aga (Chirascanni näitel), et see adapter ei pruugi seadme antud masina taga mitteolemasolul isegi veatult konstrueeruda. Seega tuleks asja ajada sellisel moel, et adapteri moodustamine algaks alles juhul, kui on selge, et ZMQ pole sätitud. Mõneti muudab see programmiteksti vist koledamaks (või kuidas seda teha saaks?), aga muidugi jätab ära tarbetut tegevust.

## 230109 

Mulle ikkagi hakkab tunduma, et võiks mingi üldise spektromeetri VI objekti ikka ka vahele pista, sest vastavat tegevust järjest koguneb. No lambda correction näiteks ja siis mingid klaviatuurishortcutid (Esc, F3, F6, F9). Ok

Sellest lambda korrektsioonist peaks arutama. Kui meil on juba see instrumendi settingu fail ehk .ini fail, siis seal saaks ka defineerida jooni. Edasi oleks vaja ühte listi, sinna võiksid ju nt. tekkida kõik need jooned, mis parasjagu pildile mahuvad ja seal peaks olema checkbox, label ja edit. Üldiselt peaks muu kõik olema saadav JYAndori eeskujul. Nii et esimene asi oleks siis saada selline listbox või -view.
Janomaitea, see spektromeetri lülitamine on ka ikka asi, et kas saaks kuidagi seda ühekordset ja vaba jooksu ikka eristada ja mis saab kineetikast ja siis et bäcki ja refi taasettemanamine peaks ka kuidagi ikka võimalik olema (et kui raadio valida, siis äkki tuleb ette ja saaks neid ka salvestada ja võib/olla ka bäcki näiteks tagasi manada, äkki mingil hetkel vaja). 

Refi nimi võiks näha olla ja siis ka võib.olla mingi kell, millal viimati bõkki võeti.

## 230116

Ja ma mõtlen nüüd, et tegelikult peaks mingi protseduuri kala ka kokku panema, et see poleks väga raske teha, s.m.e. võib-olla siis mingi baasklass ja/või checklist, kuidas parimini toimida. No kasvõi, et kui praegu ma tahaks kokku panna mingi automatiseeritud Shamrocki keeraja ja järjest mõõtja, et siis kui raskeks see asi läheb või ta tegelikult ei peakski minema.