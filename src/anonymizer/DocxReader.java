package anonymizer;

import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.Iterator;
import java.util.List;
import java.util.Set;
import java.util.regex.Pattern;
import java.util.stream.Stream;

import org.apache.poi.xwpf.usermodel.IBodyElement;
import org.apache.poi.xwpf.usermodel.XWPFDocument;
import org.apache.poi.xwpf.usermodel.XWPFParagraph;
import org.apache.poi.xwpf.usermodel.XWPFTable;
import org.apache.poi.xwpf.usermodel.XWPFTableCell;
import org.apache.poi.xwpf.usermodel.XWPFTableRow;

import init.Init;

/**
 * Reading the first table of a docx file. and saving the content of all cells
 * in an array containing unique strings
 * 
 * @author Phillip Richter-Pechanski
 *
 */
public class DocxReader {
	
	/**
	 * Extract plain text from docx file 
	 * 
	 * @param fileName: String
	 * @return textAsList: ArrayList<String>
	 */
	public static ArrayList<String> extractPlainText(String fileName) {
		ArrayList<String> textAsList = new ArrayList<String>();
		try {
			XWPFDocument doc = new XWPFDocument(new FileInputStream(fileName));
            Iterator<IBodyElement> iter = doc.getBodyElementsIterator();
            iter.next();
            while (iter.hasNext()) {
               IBodyElement elem = iter.next();
               if (elem instanceof XWPFParagraph && !((XWPFParagraph) elem).getParagraphText().isEmpty()) {
            	   textAsList.add(((XWPFParagraph) elem).getParagraphText());
               } else if (elem instanceof XWPFTable) {
            	   //System.out.println(((XWPFTable) elem).getText());
            	   for (XWPFTableRow row : ((XWPFTable) elem).getRows()) {
            		   	List<XWPFTableCell> cell = row.getTableCells();
	       				for (XWPFTableCell xwpfTableCell : cell) {
	       					String extractedCell = "";
	       					if (xwpfTableCell != null) {
	       						for (XWPFParagraph p : xwpfTableCell.getParagraphs()) {
	       							String text = p.getText();
	       							String[] tokens = text.split(" ");
	       							for (String string : tokens) {
	       								extractedCell += string + " ";
	       							}
	       						}
	       					}
		       				textAsList.add(extractedCell);
	       				}
            	   }
               }
            }
            doc.close();
                  
		} catch (FileNotFoundException e) {
			e.printStackTrace();
		} catch (IOException e) {
			e.printStackTrace();
		}
		return textAsList;
	}

	/**
	 * Extract tokens from first table in a docx file and save them in an array of Strings
	 * 
	 * @param fileName: String
	 * @return list: ArrayList<String>
	 */
	public static ArrayList<String> extractHeader(String fileName) {

		ArrayList<String> headerInfo = new ArrayList<String>();
		ArrayList<String> stopwords = new ArrayList<String>();
		ArrayList<String> excludeHeaderTokens = new ArrayList<String>();

		try (Stream<String> stream = Files.lines(Paths.get(Init.STOPWORDS))) {
			stream.forEach(line -> {
				stopwords.add(line);
			});
		} catch (Exception e) {
			e.printStackTrace();
		}
		
		try (Stream<String> stream = Files.lines(Paths.get(Init.EXCLUDE_HEADER_TOKENS))) {
			stream.forEach(line -> {
				excludeHeaderTokens.add(line.trim());
			});
		} catch (Exception e) {
			e.printStackTrace();
		}

		try {
			XWPFDocument doc = new XWPFDocument(new FileInputStream(fileName));

			List<XWPFTable> table = doc.getTables();

			List<XWPFTableRow> row = table.get(0).getRows();
			for (XWPFTableRow xwpfTableRow : row) {
				List<XWPFTableCell> cell = xwpfTableRow.getTableCells();
				for (XWPFTableCell xwpfTableCell : cell) {
					if (xwpfTableCell != null) {
						for (XWPFParagraph p : xwpfTableCell.getParagraphs()) {
							String text = p.getText();
							String[] tokens = text.split(" ");
							for (String string : tokens) {
								if (!stopwords.stream().anyMatch(str -> str.trim().equals(string.trim())) 
										&& !excludeHeaderTokens.stream().anyMatch(str -> str.trim().equals(string.trim()))) {
									headerInfo.add(string.toLowerCase());
								}
							}
						}
					}
				}
			}
			doc.close();
		} catch (FileNotFoundException e) {
			e.printStackTrace();
		} catch (IOException e) {
			e.printStackTrace();
		}
		Set<String> result = new HashSet<String>(headerInfo);
		ArrayList<String> list = new ArrayList<String>(result);
		
		// Remove numbers and short strings from the list
		String myRegex = "\\b[0-9]+\\b";
		Pattern p = Pattern.compile(myRegex);
		
		for (int i = 0; i < list.size(); i++) {
			if (p.matcher(list.get(i)).matches() | list.get(i).trim().length() <= 1) {
				list.remove(i);
			}
		}

		return list;
	}
}