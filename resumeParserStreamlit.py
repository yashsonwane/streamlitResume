import base64
import streamlit as st
import pandas as pd
from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, DataReturnMode
from ResumeEntitiesDrive import get_resume_entities
from Gdrive import get_drive_folder_list


#page layout
st.set_page_config(layout = 'wide', initial_sidebar_state='collapsed')

def show_pdf(file_path:str):
    """Show the PDF in Streamlit
    That returns as html component

    Parameters
    ----------
    file_path : [str]
        Uploaded PDF file path
    """
    with open(file_path, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode("utf-8")
    pdf_display = f'<embed src="data:application/pdf;base64,{base64_pdf}" width="100%" height="1000" type="application/pdf">'
    st.markdown(pdf_display, unsafe_allow_html=True)


def main():
    """Streamlit application"""

    st.title("Discite Demo-Resume Parser ")
    
    # uploaded_file = st.file_uploader("Choose your .pdf file", type="pdf")
    flag=None
    
    results = []
    results_location=[]
    results_skill=[]
    results_year=[]

    # url = "https://share.streamlit.io/mesmith027/streamlit_webapps/main/MC_pi/streamlit_app.py"
    # st.write("[link](%s)" % url)
   
    #geting drive resume
    st.subheader("Drive link")
    with st.form(key="link", clear_on_submit=True):
        
        dff = pd.DataFrame()
        first, second, third = st.columns(3)
        drive_link = first.text_input('Drive Link:')

        submitted = st.form_submit_button("Generate ")

        if submitted:
            
            drive_link =drive_link.split("/")
            folder=drive_link[-1].strip()
            print(folder)
            try:
                drive_list_df=get_drive_folder_list(folder)
            except:
                pass
            print(drive_list_df)
            flag=get_resume_entities(drive_list_df)
            print("drive dateset")
                
    #Selecting dataset
    st.subheader("Which Dataset you want to select")
    genre = st.radio(
        "",
        ('Discite Analytics dataset', 'Google Drive dataset'))


    st.subheader("Search Feature")

    with st.form(key="data", clear_on_submit=True):
        dff = pd.DataFrame()
        first, second, third,fourth = st.columns([2,2,1,1])
        location_search = first.text_input('Location:').lower()
        skills_search = second.text_input('Skills:').lower()
        min_year_of_exp_search = third.text_input('Minimun Years of Exprience:').lower()
        max_year_of_exp_search = fourth.text_input('Maximun Years of Exprience:').lower()


        #convert input to None if data is not present
        if len(location_search) == 0:
            location_search=None
        if len(skills_search) == 0:
            skills_search=None
        if len(min_year_of_exp_search) == 0:
            min_year_of_exp_search=0
        if len(max_year_of_exp_search) == 0:
            max_year_of_exp_search=100

        

        submitted = st.form_submit_button("Submit")

        if submitted:

            if genre == 'Discite Analytics dataset':
                df_entities=pd.read_csv("enti.csv")
                st.write('You selected Discite analytics Dataset.')
            else:
                try:
                    df_entities=pd.read_csv("NewDriveResumeEntities.csv")
                    print("working on drive csv")
                    st.write("You selected Google Drive Dataset.")
                except Exception as e:
                    print(e)
                    st.error("Please first create Google Drive dataset ")

            #read temp.csv
            

            try:
                for i in range(len(df_entities)):
                    try:
                        for location_s in location_search.split(","):
                            if any([(location_s in i) for i in eval(df_entities.iloc[i].Location) if len(location_s) >=3]):
                                results.append(df_entities.iloc[i])
                                
                    except:
                        pass
                    try:
                        for skills_s in skills_search.split(","):
                            if any([(skills_s in i) for i in eval(df_entities.iloc[i].Skills) if len(skills_s) >=3]):
                                results.append(df_entities.iloc[i])
                    except:
                        pass
                    try:
                        
                        if int(min_year_of_exp_search) <= df_entities.iloc[i].Year_of_exp <= int(max_year_of_exp_search):
                            results.append(df_entities.iloc[i])
                    except:
                        pass
                    
                
                # if results_skill and results_location:

                dff=pd.DataFrame(results)
                dff=dff.drop_duplicates(keep='first')
            except:
                pass
                
            try:
                gb = GridOptionsBuilder.from_dataframe(dff)
                gb.configure_pagination(paginationAutoPageSize=True) #Add pagination
                gb.configure_side_bar() #Add a sidebar
                gb.configure_selection('multiple', use_checkbox=True, groupSelectsChildren="Group checkbox select children") #Enable multi-row selection
                gridOptions = gb.build()
            

                grid_response = AgGrid(
                                        dff,
                                        gridOptions=gridOptions,
                                        data_return_mode='AS_INPUT', 
                                        update_mode='MODEL_CHANGED', 
                                        fit_columns_on_grid_load=False,
                                        theme='blue', #Add theme color to the table
                                        enable_enterprise_modules=True,
                                        height=350, 
                                        width='100%',
                                        reload_data=True
                                    )

            
                
                selected = grid_response['selected_rows'] 
                df = pd.DataFrame(selected) #
            except:
                pass



if __name__ == "__main__":
    main()

