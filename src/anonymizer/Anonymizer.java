package anonymizer;

import java.util.stream.Stream;

import java.util.List;
import java.io.BufferedWriter;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.StandardOpenOption;
import java.util.ArrayList;
import java.util.Arrays;

import init.Init;

/**
 * 
 * This class anonymizes a given docx file with a table header containing contact informations and returns the anonymized file 
 * with NE as placeholders. 'Peter Pan lives in London' becomes '<PER> <PER> lives in <LOC>'
 * 
 * @author Phillip Richter-Pechanski
 *
 */
public class Anonymizer {
	// Replace token if class label is one of the following:
	private static List<String> NAMED_ENTITIES = Arrays.asList("PER", "LOC", "EMAIL", "URI", "PLZ", "DATE",
			"PHONE", "SALUTE", "TITLE");
	private ArrayList<String> headerTokens;
	private String output;
	private String docFile;
	private ArrayList<String> docAsTxt;
	private ArrayList<String> annotatedText;
	private static String SEPERATOR = "/";

	private static final double f_errorRatioThreshold = 0.33334;

	/**
	 * Constructor
	 * 
	 * @param docFile: String
	 * @param output: String
	 * @throws IOException
	 */
	public Anonymizer(String docFile, String output) throws IOException {
		this.docFile = docFile;
		this.headerTokens = DocxReader.extractHeader(docFile);
		this.docAsTxt = DocxReader.extractPlainText(docFile);
		this.output = output;
		this.annotatedText = NamedEntityRecognizer.run(docAsTxt);
	}
	
	/**
	 * Minimum Edit Distance (LevenshteinDistance)
	 * Implements Yuwono, Kester et al. 2016
	 * 
	 * @param lhs: CharSequence
	 * @param rhs: CharSequence
	 * @return cost: int
	 */
	public static int levenshteinDistance(CharSequence lhs, CharSequence rhs) {
		int len0 = lhs.length() + 1;
		int len1 = rhs.length() + 1;

		// the array of distances
		int[] cost = new int[len0];
		int[] newcost = new int[len0];

		// initial cost of skipping prefix in String s0
		for (int i = 0; i < len0; i++)
			cost[i] = i;

		// dynamically computing the array of distances

		// transformation cost for each letter in s1
		for (int j = 1; j < len1; j++) {
			// initial cost of skipping prefix in String s1
			newcost[0] = j;

			// transformation cost for each letter in s0
			for (int i = 1; i < len0; i++) {
				// matching current letters in both strings
				int match = (lhs.charAt(i - 1) == rhs.charAt(j - 1)) ? 0 : 1;

				// computing cost for each transformation
				int cost_replace = cost[i - 1] + match;
				int cost_insert = cost[i] + 1;
				int cost_delete = newcost[i - 1] + 1;

				// keep minimum cost
				newcost[i] = Math.min(Math.min(cost_insert, cost_delete), cost_replace);
			}

			// swap cost/newcost arrays
			int[] swap = cost;
			cost = newcost;
			newcost = swap;
		}

		// the distance is the cost for transforming all letters in both strings
		return cost[len0 - 1];
	}

	// =======================================================================================================

	
	/**
	 * Decide if a token needs to be anonymized as spelling variant
	 * 
	 * @param tokenName: String
	 * @param tokenText: String
	 * @return isPatientName: Boolean
	 */
	private static Boolean anonymizeName(String tokenName, String tokenText) {
		boolean isPatientName = false;
		int editDistance = levenshteinDistance(tokenText.toLowerCase(), tokenName.toLowerCase());
		int nameTokenLength = tokenName.length();
		int tokenLength = tokenText.length();
		int minimumTokenLength = Math.min(tokenLength, nameTokenLength);
		double errorRatio = (double) editDistance / (double) minimumTokenLength;
		if (errorRatio <= f_errorRatioThreshold) {
			isPatientName = true;
		}
		return isPatientName;
	}

	
	/**
	 * Read stopwords into array
	 * 
	 * @return stopwords: ArrayList<String>
	 */
	private static ArrayList<String> stopwordList() {
		ArrayList<String> stopwords = new ArrayList<String>();
		try (Stream<String> stream = Files.lines(Paths.get(Init.STOPWORDS))) {
			stream.forEach(line -> {
				stopwords.add(line);
			});
		} catch (IOException e) {
			e.printStackTrace();
		}
		return stopwords;
	}
	
	/**
	 * Read suffixlist into array
	 * 
	 * @return suffixes: ArrayList<String>
	 */
	private static ArrayList<String> extractsuffixes() {
		ArrayList<String> suffixes = new ArrayList<String>();
		try (Stream<String> stream = Files.lines(Paths.get(Init.SUFFIXES_STREETS))) {
			stream.forEach(line -> {
				suffixes.add(line);
			});
		} catch (IOException e) {
			e.printStackTrace();
		}
		try (Stream<String> stream = Files.lines(Paths.get(Init.SUFFIXES_TOWNS))) {
			stream.forEach(line -> {
				suffixes.add(line);
			});
		} catch (IOException e) {
			e.printStackTrace();
		}

		return suffixes;
	}

	
	/**
	 * Takes anonymized text as array and writes it to textfile
	 * 
	 * @param path: Path
	 * @param anonNotes: ArrayList<ArrayList<String>>
	 */
	private static void writeAnonymizedFile(Path path, ArrayList<ArrayList<String>> anonNotes) {
		BufferedWriter writer;
		try {
			writer = Files.newBufferedWriter(path);
			for (ArrayList<String> line : anonNotes) {
				if (line.size() == 1 && line.get(0).equals("\n")) {
					writer.append(System.lineSeparator());
				} else {
					writer.append(String.join(" ", line) + System.lineSeparator());
				}
			}
			writer.close();
		} catch (IOException e) {
			e.printStackTrace();
		}
	}

	/**
	 * Anonymization pipeline
	 * Outputs anonymized text in plain text
	 * Outputs text labeled with NE in ConLL 2002 format
	 * Outputs text labeled with (<KEEP>, <ANON>) in CoNLL 2002 format 
	 * Outputs text in CoNLL 2002 format
	 * 
	 */
	public void anonymizeAdmissionNotes() {
		System.out.println("Processing file: " + this.docFile);
		ArrayList<ArrayList<String>> anonNotes = new ArrayList<ArrayList<String>>();
		// Read array and anonymize tokens
		for (String line : annotatedText) {
			String lines[] = line.split(" ");
			// Check if line is empty
			if (lines.length >= 1 && !lines[0].trim().isEmpty()) {
				ArrayList<String> fullLine = new ArrayList<String>();
				// Parse each line of the file
				for (String token : lines) {
					int i = token.lastIndexOf(SEPERATOR);
					String[] entities = { token.substring(0, i), token.substring(i + 1) };
					String labeled = entities[0] + "\t" + entities[1] + System.lineSeparator();
					try {
						Files.write(Paths.get(this.output+".tokenized"), labeled.getBytes(), StandardOpenOption.CREATE, StandardOpenOption.APPEND);
					} catch (IOException e) {
						e.printStackTrace();
					}
					if (entities.length > 1) {
						// Split token and entities
						Boolean skipping = false;
						//System.out.println(entities[0] + " " + entities[1]);
						
						for (String name : this.headerTokens) {
							// Check if Spelling Anonymizer finds a token to anonymize, check that it is not
							// a stopword
							if (anonymizeName(name, entities[0]) && !stopwordList().stream()
									.anyMatch(str -> str.trim().equals(entities[0].toLowerCase()))) {
								//System.out.println("-> SPELL");
								fullLine.add("<" + entities[1] + ">");
								skipping = true;
								try {
									String anonym = entities[0] + " " + "<ANON_SPELL>" + System.lineSeparator();
									Files.write(Paths.get(this.output+".tokenized_anon"), anonym.getBytes("UTF-8"), StandardOpenOption.CREATE, StandardOpenOption.APPEND);
								} catch (IOException e) {
									e.printStackTrace();
								}
								break;
							}

						}
						
						//skipping = false;
						// Token is not in header, but is a NE from list NAMED_ENTITIES and is not a
						// stopword
						if ((!skipping && NAMED_ENTITIES.stream().anyMatch(str -> str.trim().equals(entities[1]))
								&& !stopwordList().stream().anyMatch(str -> str.trim().equals(entities[0].toLowerCase())))
							) {
							//System.out.println("-> anon " + entities[0] + " " + entities[1]);
							fullLine.add("<" + entities[1] + ">");
							try {
								//System.out.println("->NE" + entities[1]);
								String anonym = entities[0] + " " + "<ANON_NE>" + System.lineSeparator();
								Files.write(Paths.get(this.output+".tokenized_anon"), anonym.getBytes("UTF-8"), StandardOpenOption.CREATE, StandardOpenOption.APPEND);							} catch (IOException e) {
									}
						} else if (!skipping && extractsuffixes().stream().anyMatch(str -> entities[0].toLowerCase().trim().endsWith(str.toLowerCase()))) {
							fullLine.add("<LOC>");
							try {
								//System.out.println("->SUFFIX");
								String anonym = entities[0] + " " + "<ANON_SUFFIX>" + System.lineSeparator();
								Files.write(Paths.get(this.output+".tokenized_anon"), anonym.getBytes("UTF-8"), StandardOpenOption.CREATE, StandardOpenOption.APPEND);							} catch (IOException e) {
							}
						
						} else if (!skipping) {
							String anonym = entities[0] + " " + "<KEEP>" + System.lineSeparator();
							try {
								Files.write(Paths.get(this.output+".tokenized_anon"), anonym.getBytes("UTF-8"), StandardOpenOption.CREATE, StandardOpenOption.APPEND);
							} catch (IOException e) {
								e.printStackTrace();
							}
							fullLine.add(entities[0]);
						}
						String anonym = entities[0] + " " + "O" + System.lineSeparator();
						try {
							Files.write(Paths.get(this.output + ".conll"), anonym.getBytes("UTF-8"), StandardOpenOption.CREATE, StandardOpenOption.APPEND);
						} catch (IOException e) {
							e.printStackTrace();
						}
					}
				}
				anonNotes.add(fullLine);
			} else {
				anonNotes.add(new ArrayList<String>(Arrays.asList("\n")));
			}
		}
		Path path = Paths.get(this.output);
		writeAnonymizedFile(path, anonNotes);
	}
}
