from PIL import Image
from pytesseract import pytesseract
import os, csv, cv2 
import numpy as np

class Stoa2CSV: 
    def __init__(self, csv_path="postings.csv", tessaract_path="tesseract"):
        self.csv_path = csv_path
        self.tessaract_path = tessaract_path
        pytesseract.tesseract_cmd = tessaract_path 

    def clean_image(self, image_path):
        image = cv2.imread(image_path)
        # image = cv2.resize(image, None, fx=2, fy=2)
        # image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # kernel = np.ones((1,1), np.uint8)

        # cv2.imwrite("cleaned.png", image)
        return(image)

    def extract_text(self, image):
        # image = Image.open(image)
        image = self.clean_image(image)

        text = pytesseract.image_to_string(
            image,
            output_type=pytesseract.Output.DICT    
        )

        return(text)

    def clean_text(self, text):
        output = text["text"] # enter the text part 
        output = os.linesep.join([s for s in output.splitlines() if s]) # remove newlines
        output = output.replace("  ", " ") # remove double spaces
        output = output.splitlines() # convert string to list of strings 
        output = list(filter(str.strip, output)) # remove empty strings

        return(output)

    def process_StoaLD(self, text):
        output = self.clean_text(text)

        format = output[0] # format
        round  = output[1] # round
        date   = output[2] # date
        flight = output[3] # flight

        counter = 5 # start at 5 because the first 5 lines are not relevant
        rounds = {} # dictionary to store the rounds
        while True: 
            try: 
                debate = output[counter].split(" ") # room, club, aff, club neg
                # room_club_aff_club_neg[0 : 1] = [''.join(room_club_aff_club_neg[0 : 1])] # combine room and number

                rounds.update({f"debate{counter-4}": { 
                    "room": f"{debate[0]} {debate[1]}",
                    "AFF_club": debate[2],
                    "AFF": debate[3] + " " + debate[4],
                    "NEG_club": debate[5],
                    "NEG": debate[5] + " " + debate[6]
                }})

                counter = counter + 1

            except IndexError:
                try: 
                    debate = output[counter].split(" ") # room, club, aff, club neg
                except IndexError:
                    pass
                
                # The second section of FLIGHT two is messing up results, skip over this
                if "FLIGHT" in debate: 
                    counter = counter + 1
                
                # we're probably at the end of the list, so break
                else:
                    break 

        # for key, value in rounds.items():
        #     print(value)


        return(rounds)

    def write_postings(self, rounds): 
      
        with open(self.csv_path, "w", newline="") as csvfile:
            writer = csv.DictWriter(
                csvfile, 
                fieldnames=["round", "room", "AFF_club", "AFF", "NEG_club", "NEG"]
            )

            writer.writeheader()

            for key, value in rounds.items():
                print(value)
                writer.writerow({
                    "round": "2",
                    "room": value["room"],
                    "AFF_club": value["AFF_club"],
                    "AFF": value["AFF"],
                    "NEG_club": value["NEG_club"],
                    "NEG": value["NEG"]
                })

if __name__ == '__main__':
    stoa2csv = Stoa2CSV("LD.csv")
    text = stoa2csv.extract_text("postings/LD.png")
    rounds = stoa2csv.process_StoaLD(text)
    stoa2csv.write_postings(rounds)
    # print(output)