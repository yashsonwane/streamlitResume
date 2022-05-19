import glob
import os,io
import time
import pandas as pd
import streamlit as st
from google.cloud import vision_v1
from pdf2image import convert_from_path
from resparser import resumeparser
from Gdrive import get_shareable_link,download_file
from Google import Create_Service

CLIENT_SECRET_FILE = r'client_secrets.json'
API_NAME = 'drive'
API_VERSION = 'v3'
SCOPES = ['https://www.googleapis.com/auth/drive']


service = Create_Service(CLIENT_SECRET_FILE, API_NAME, API_VERSION, SCOPES)

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = r'vision_api\vision_api_key.json'
client = vision_v1.ImageAnnotatorClient()

def get_resume_entities(drive_df):

    entities_df=pd.DataFrame(columns=('Name','Location','Year_of_exp','Skills','Email','Mobile','shareable_link'))
    #progress bar
    my_bar = st.progress(0)
    percentage_complete=0
    step=100//len(drive_df)
    st.subheader("Reading Resumes..........")
    for drive_counter in range(len(drive_df)):

        file_id=drive_df.iloc[drive_counter]['id']
        file_name=drive_df.iloc[drive_counter]['name']
        file_type=drive_df.iloc[drive_counter]['mimeType']
        try:
                
            print(f"Itteration {drive_counter} \n")

            shareable_link=get_shareable_link(file_id)
            download_file(file_id,file_name)

            
            [stem, ext] = os.path.splitext(file_name)

            if ext == '.pdf' or ext == '.PDF' :
                    
                images = convert_from_path(f"./temp/{file_name}",500,fmt='png',poppler_path=r'poppler-0.68.0\bin')
                print(type(images[0]))
                for i, image in enumerate(images):
                    fname = 'image' + str(i) + '.png'
                    image.save(fr'temp\{fname}', "PNG")
                abc = []
                try:
                        
                    for j in range(i + 1):

                        with io.open(r'temp\image' + str(j) + '.png', 'rb') as image_file:
                            content = image_file.read()

                        image = vision_v1.types.Image(content=content)
                        response = client.text_detection(image=image)
                        texts = response.text_annotations
                        # print(texts)
                        df = pd.DataFrame(columns=['locale', 'description'])
                        for text in texts:
                            df = df.append(
                                dict(
                                    locale=text.locale,
                                    description=text.description
                                ),
                                ignore_index=True
                            )
                            
                        pdf_contents = df['description'][0]
                        abc.append(pdf_contents)
                        tesxt = abc[0].replace("\n", " ")
                        # print(tesxt)
                    entity = resumeparser(tesxt)

                    #add shareable link 
                    entity['shareable_link']=shareable_link
                    print(entity)
                                      
                except Exception as e:
                    print(e)
                    pass
                entities_df=entities_df.append(entity,ignore_index = True)
            print(f"Itteration {drive_counter} End \n")
            #Remove all temp files
            files = glob.glob(r'temp\*')
            for f in files:
                os.remove(f)
        except:
            pass

        #streamlit code
        time.sleep(0.1)
        my_bar.progress(percentage_complete + step)
        percentage_complete+=step

    try:
        entities_df.drop("None",axis=1,inplace=True)
    except Exception as e:
        print("entities_df does not contain None Cloumn")
    st.subheader("Done")
    entities_df.to_csv("NewDriveResumeEntities.csv",index=False)
    
    return True



