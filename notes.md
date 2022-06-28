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
* r välja tuua
* fitijoone värvus
* ja hakata vaatama, mis juhul teda mõtet on
* siis edasi, et fitipiirkonda täpsustada (seda võiks isegi jooksvalt saada?)
* ja kas saaks kaks paralleelset teha?
* miks seal VI-s mõned asjad enabled-disabled vilguvad?
* Andori tagasitoomise nupp ja ta võiks fitiaknaga koos ära kaduda.