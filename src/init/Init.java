package init;

import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.stream.Stream;
import java.net.*;

import anonymizer.Anonymizer;

public class Init  {
	
	public static String STOPWORDS;
	public static String REGEXNER;
	public static String NER_MODEL;
	public static String POS_MODEL;
	public static String EXCLUDE_HEADER_TOKENS;
	public static String SUFFIXES_STREETS;
	public static String SUFFIXES_TOWNS;
	
	static {
		// Define location of resource files
		STOPWORDS = "misc" + File.separator + "stopwordlist_de.txt";
		REGEXNER = "misc" + File.separator + "regex_mappings_surnames.txt,misc" + File.separator + "regex_mappings_general.txt,misc" + File.separator + "regex_mappings_towns_and_villages.txt,misc" + File.separator + "regex_mappings_streets_with_numbers_and_abr.txt,misc" + File.separator + "regex_mappings_international_firstnames.txt";
		NER_MODEL = "misc" + File.separator + "ner-model-gazeteer_conll_germaner_ep_withoutMISC.gaz.ser.gz";
		POS_MODEL = "edu" + File.separator + "stanford" + File.separator + "nlp" + File.separator + "models" + File.separator + "pos-tagger" + File.separator + "german" + File.separator + "german-hgc.tagger";
		EXCLUDE_HEADER_TOKENS = "misc" + File.separator + "header_tokens.txt";
		SUFFIXES_STREETS = "misc" + File.separator + "suffixes_streets.txt";
		SUFFIXES_TOWNS = "misc" + File.separator + "suffixes_towns.txt";
	}
	
	public static void main(String[] args) throws IOException {		
		if (args.length !=1) {
		      System.err.println("Usage: Anonymize <path to docx files>");
		      System.exit(1);
		    }
		try (Stream<Path> paths = Files.walk(Paths.get(args[0]))) {
		      paths.skip(1).filter(file -> file.toString().endsWith("docx")).forEach(file -> {
					Anonymizer ano;
				try {
					// Creates an instance of the Anonymizer class and executes the pipeline
					ano = new Anonymizer(file.toString(), file.toString()+".anon");
			  		ano.anonymizeAdmissionNotes();
				} catch (Exception e) {
					e.printStackTrace();
				}
		      });
		    } catch (IOException e) {
		      e.printStackTrace();
		    }
		
		System.out.println("De-Identification finished.");

	}
}
