# De-identification tool for German medical texts
---

This is a prototype of a de-identification pipeline for German medical admission notes from the cardiology domain. It uses a three step approach to de-identificate medical texts:
1. Rule based approach using Stanford RegexNER
2. Spelling variant detection using Yuwono's approach based on levenshtein distance
3. Stanford NER based on an out of domain trained model

This tool is am eclipse project. There is currently no runnable JAR file available.

### Prerequisities
- Java 8
- Eclipse (tested with oxygen)
- Stanford CoreNLP 3.8
    - stanford-corenlp-3.8.0.jar
- Stanford CoreNLP German models 3.8
    - stanford-germn-corenlp-2017-06-09-models.jar
- Apache POI 3.17
    - poi-2.17.jar (included)
    - poi-ooxml-3.17.jar (included)
    - poi-ooxml--schemas-3.17.jar (included)
    - xmlbeans-2.6.0.jar (included and part of Apache poi package)
- Gazetteers (included)

#### optional
- (Cureently the algorithm is configured with the default NER model)
- self trained Stanford NER model
- copy this jar into the misc/ Folder
- define the folder path to the model in Init class line 27
- if you use the default model comment line 38 in NamedEntityRecognizer class. Add to line 39:

```java		
String serializedClassifier = "edu" + File.separator + "stanford" + File.separator + "nlp" + File.separator + "models" + File.separator + "ner" + File.separator + "german.conll.hgc_175m_600.crf.ser.gz";
```


The Stanford models are available [here](https://stanfordnlp.github.io/CoreNLP/download.html)

Copy both jar files (stanford-corenlp-3.8.0.jar and stanford-germn-corenlp-2017-06-09-models.jar) into the src/lib/ directory

### Installation

- Open Eclipse
- *File* -> *Import*
- Choose *General - Existing Project into Workspace*
- Select folder and click  *Finish*

### Performaing de-identification task

- You can start the program inside eclipse. To do so, open the Init class in the init package. Right click in the code and choose *Run configuration*. 
- Now click on the "Arguments tab" and enter the Location of the docx files. The program will output the following files into the Folder of the docx files:
    - Outputs anonymized text in plain text
    - Outputs text labeled with NE in ConLL 2002 format
    - Outputs text labeled with (KEEP, ANONYMIZE) in CoNLL 2002 format 
    - Outputs text in CoNLL 2002 format

### Example 

##### Input 

This is an example input/output of the pipeline. For further output files and an example docx file see folder *example/*.

```
Frau Maria Mustermann, whf. in 10000 Musterstadt, Musterstr, 12a, ist am 01.02.1999 in unserer Ambulanz aufgenommen worden.
```

#### output

```
<SALUTE> <PER> <PER>, whf. in <PLZ> <LOC>, <LOC> <LOC>, ist am <DATE> in unserer Ambulanz aufgenommen worden.
```

### Folder structure

```bash
├── src (pipeline)
│   ├── init (execution and resource configuration)
│   ├── anonymizer (Pipeline modules)
├── lib (dependencies)
├── misc (resource files)
├── example (example docx input, de-identified and annotated CoNLL 2002 output files)
├── Reports (Reports, presentation)
├── evaluation (python template for evaluation purposes)
├── python_anon (alternative python de-identificator)
```

### Running the jar file

To be independent from eclipse, you can create a jar file.
- Click on File -> Export -> Runnable Jar
- Choose an export destination
- Choose 'Package required libraries into generated jar'
- Click on Finish

To execute the program copy the misc/ folder into the same destination where your jar is. You can execute the file, if you named it anonymizer.jar, like this:

```bash
anonymizer.jar <path to docx files>
```

### Classes

- **Init**: The initializing class containing important resource configurations. For execution it Needs one Argument: <path to docx files>
- **Anonymizer**: This class anonymizes a given docx file with a table header containing contact informations and returns the anonymized file with NE as placeholders. 'Peter Pan lives in London' becomes '<PER> <PER> lives in <LOC>'
- **DocxReader**: Reading the first table of a docx file. and saving the content of all cells in an array containing unique strings
- **NamedEntityRecognizer**: Loads the Stanford CoreNLP pipeline and annotates a given array of strings    

### References
- Yuwono, Steven Kester, Hwee Tou Ng, and Kee Yuan Ngiam. 2016. “AutomatedAnonymization as Spelling Variant Detection.” InProceedings of the ClinicalNatural Language Processing Workshop (ClinicalNLP),99–103. Osaka, Japan:The COLING 2016 Organizing Committee, December.http://aclweb.org/anthology/W16-4214.
- Manning, Christopher D., Mihai Surdeanu, John Bauer, Jenny Finkel, Prismatic Inc,Steven J. Bethard, and David Mcclosky. 2014. “The Stanford CoreNLP NaturalLanguage Processing Toolkit.” InIn Proceedings of the 52nd Annual Meeting ofthe Association for Computational Linguistics: System Demonstrations,55–60.
