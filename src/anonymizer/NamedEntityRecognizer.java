package anonymizer;

import edu.stanford.nlp.ling.CoreAnnotations.SentencesAnnotation;
import edu.stanford.nlp.ling.CoreAnnotations.TextAnnotation;
import edu.stanford.nlp.ling.CoreAnnotations.TokensAnnotation;
import edu.stanford.nlp.ling.CoreLabel;
import edu.stanford.nlp.ling.CoreAnnotations.NamedEntityTagAnnotation;
import edu.stanford.nlp.util.CoreMap;

import java.io.File;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;
import java.util.Properties;
import edu.stanford.nlp.pipeline.*;

import init.Init;

/**
 * @author Phillip Richter-Pechanski
 * 
 * Loads the Stanford CoreNLP pipeline and annotates a given array of strings
 *
 */
public class NamedEntityRecognizer {

	/**
	 * Takes an input text array, loads the Stanford CoreNLP pipeline and annotates the text.
	 * 
	 * @param input: ArrayList<String>
	 * @return output: ArrayList<String>
	 * @throws IOException
	 */
	public static ArrayList<String> run(ArrayList<String> input) throws IOException {
		ArrayList<String> output = new ArrayList<String>();
		// creates a StanfordCoreNLP object, with POS tagging, lemmatization, NER,
		// parsing, and coreference resolution
		//String serializedClassifier = Init.NER_MODEL;
		String serializedClassifier = "edu" + File.separator + "stanford" + File.separator + "nlp" + File.separator + "models" + File.separator + "ner" + File.separator + "german.conll.hgc_175m_600.crf.ser.gz";
		
		String posModel = Init.POS_MODEL;

		Properties props = new Properties();
		props.put("annotators", "tokenize, ssplit, pos, lemma, ner, regexner");
		props.put("ner.model", serializedClassifier);
		props.put("pos.model", posModel);
		props.put("tokenize.language", "de");
		props.put("ssplit.isOneSentence", "true");
		props.put("ssplit.language", "de");
		props.put("lemma.language", "de");
		props.put("regexner.mapping", Init.REGEXNER);
		StanfordCoreNLP pipeline = new StanfordCoreNLP(props);

		for (String line : input) {
			// create an empty Annotation just with the given text
			if (line.trim().length() > 0) {
				Annotation document = new Annotation(line);
				String annotatedLine = annotate(pipeline, document);
				output.add(annotatedLine);
			}
		}
		return output;
	}

	
	/**
	 * Takes the CoreNLP pipeline and the Annotation document and returns the text annotated
	 * 
	 * @param pipeline: StanfordCoreNLP
	 * @param document: Annotation
	 * @return output: String
	 */
	public static String annotate(StanfordCoreNLP pipeline, Annotation document) {
		String output = "";
		// run all Annotators on this text
		pipeline.annotate(document);
		List<CoreMap> sentences = document.get(SentencesAnnotation.class);
		
		for (CoreMap sentence : sentences) {
			// traversing the words in the current sentence
			// a CoreLabel is a CoreMap with additional token-specific methods
			for (CoreLabel token : sentence.get(TokensAnnotation.class)) {
				// this is the text of the token
				String word = token.get(TextAnnotation.class);
				// this is the NER label of the token
				String ne = token.get(NamedEntityTagAnnotation.class);
				output += word + "/" + ne + " ";
			}
		}
		return output;
	}
}