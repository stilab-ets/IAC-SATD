import subprocess
from pathlib import Path

from RQ1_Taxonomy_Construction.SATD_collector.CommentsMining.CommentExtractor import remove_newlines
from RQ1_Taxonomy_Construction.SATD_collector.CommentsMining.SatdKeyWordLists import keywordList1, keywordList2



# === DYNAMIC CLASS PATH FOR JAVA ===
PROJECT_ROOT = Path(__file__).resolve().parent.parent  # points to test_satd_1
LIBS_DIR = PROJECT_ROOT / "libs"

WEKA_LIB = LIBS_DIR / "weka/current/jar"
CLI_LIB = LIBS_DIR / "commons-cli"
SATD_JAR = LIBS_DIR / "satd_detector.jar"

classpath = ":".join(
    [str(jar) for jar in WEKA_LIB.glob("*.jar")] +
    [str(jar) for jar in CLI_LIB.glob("*.jar")] +
    [str(SATD_JAR)]
)
# === END OF CLASS PATH SETUP ===


class SATDDetector:

    def detect(self):
        pass  # This method will be overridden by subclasses bellow


class KeywordList1Detector(SATDDetector):
    def detect(self, comments):
        satdComments=[]
        for i in range(len(comments) - 1, -1, -1):
            if is_satd_comment_1(comments[i][0].lower()) == 1:
                satdComments.append(comments[i])
                comments.pop(i)
        
        satdComments.reverse()

        return satdComments
    

class KeywordList2Detector(SATDDetector):
    def detect(self, comments):
        satdComments=[]
        for i in range(len(comments) - 1, -1, -1):
            if is_satd_comment_2(comments[i][0].lower()) == 1:
                satdComments.append(comments[i])
                comments.pop(i)
        
        satdComments.reverse()
        return satdComments
    


class KeywordListsDetector(SATDDetector):
    def detect(self, comments):
        satdComments=[]
        for i in range(len(comments) - 1, -1, -1):
            if is_satd_comment_3(comments[i][0].lower()) == 1:
                satdComments.append(comments[i])
                comments.pop(i)
        
        satdComments.reverse()
        return satdComments



class MLModelDetector(SATDDetector):
    def detect(self, comments):

        satdComments = []
        i = 0

        # Path to the JAR
        PROJECT_ROOT = Path(__file__).resolve().parent.parent  # points to test_satd_1
        SATD_JAR = PROJECT_ROOT / "libs" / "satd_detector.jar"

        while i < len(comments):
            print(comments[i][0])
            interm = remove_newlines(comments[i][0])

            # Java command using -jar and --add-opens
            command = [
                "java",
                "--add-opens", "java.base/java.lang=ALL-UNNAMED",
                "-jar", str(SATD_JAR),
                "test"  # trigger test mode
            ]

            try:
                # Run Java and send the comment as input
                result = subprocess.run(
                    command,
                    input=interm + "\n/exit\n",  # /exit ends the Java test mode for this comment
                    capture_output=True,
                    text=True,
                    timeout=3
                )

                output = result.stdout.strip()
                print("Java output:\n", output)

                # Parse SATD result
                if ">SATD" in output:
                    print("SATD detected")
                    satdComments.append(comments[i])
                    comments.remove(comments[i])
                elif ">Not SATD" in output:
                    print("Not SATD detected")
                else:
                    print("Unknown output")
            except subprocess.TimeoutExpired:
                print("Java process timed out for comment:", interm)
            except Exception as e:
                print("Error running Java:", e)

            i += 1

        return satdComments


def is_satd_comment_1(comment):
    # Filtrer les commentaires qui contiennent au moins un mot de word_list
    if any(word in comment for word in keywordList1):
        return 1
    return 0 


def is_satd_comment_2(comment):
    # Filtrer les commentaires qui contiennent au moins un mot de word_list
    if any(word in comment for word in keywordList2):
        return 1
    return 0 


def is_satd_comment_3(comment):
    # Filtrer les commentaires qui contiennent au moins un mot de word_list
    if any(word in comment for word in keywordList1) or any(word in comment for word in keywordList2):
        return 1
    return 0 