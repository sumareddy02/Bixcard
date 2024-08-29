#%%writefile my_app.py

import streamlit as st
from streamlit_option_menu import option_menu
import easyocr
from PIL import Image
import pandas as pd
import numpy as np
import re
import io
import sqlite3


def image_to_text(path):
  input_img=Image.open(path)

  # converting image to array format

  image_arr=np.array(input_img)

  reader=easyocr.Reader({'en'}) #en is english language in which we read data
  text=reader.readtext(image_arr,detail=0) # if we give details =0 it shows only text format data not array data
  return text,input_img

def extracted_text(texts):
  extracted_dict={ "Name" : [],
                  "Designation":[],
                  "Company_Name":[],
                  "Contact":[],
                  "Email":[],
                  "Website":[],
                  "Address":[],
                  "Pincodes":[]
  }

  extracted_dict["Name"].append(texts[0])
  extracted_dict["Designation"].append(texts[1])

  for i in range (2,len(texts)):
    if texts[i].startswith("+") or "-" in texts[i]:
      extracted_dict["Contact"].append(texts[i])

    elif "@" in texts[i] and ".com" in texts[i]:
      extracted_dict["Email"].append(texts[i])

    elif "WWW" in texts[i] or "www" in texts[i] or "www" in texts[i] or "wWw" in texts[i] or "wwW" in texts[i]:
      small=texts[i].lower()
      extracted_dict["Website"].append(texts[i])

    elif "Tamil Nadu" in texts[i] or "TamilNadu" in texts[i] or texts[i].isdigit():
      extracted_dict["Pincodes"].append(texts[i])

    elif re.match(r'^[A-Za-z]',texts[i] ):
      extracted_dict["Company_Name"].append(texts[i])

    else:
      remove_colon=re.sub(r'[,;]','',texts[i])
      extracted_dict["Address"].append(texts[i])

  for key,value in extracted_dict.items():
    #print(key,":",value)
    if len(value)>0:
      concatenate="".join(value)
      extracted_dict[key]=[concatenate]
    else:
      value="NA"
      extracted_dict[key]=[value]

  return extracted_dict



# streamlit part
st.set_page_config(layout="wide")
st.title("EXTRACTING BUSINESS CARD DATA WITH 'OCR'")

#with st.sidebar:
 # select=option_menu("Main Menu ",["Home","Uplod and Modify","Delete"])

tab1,tab2,tab3=st.tabs(["Home","Uplod and Modify","Delete"])
#if select=="Home":
with tab1:

  st.markdown("### :blue[**Technologies Used :**] Python,easy OCR,Streamlit,SQLITE3,Pandas")

  st.markdown("### :green[**About :**] Bizcard is a Python application designed to extract information from business cards. ")

  st.write('### The main purpose of Bizcard is to automate the process of extracting key details from business card images,such as name , designation, company,contact information,and other relevant data.By leveraging the power of OCR(Optical character Recognition) provided by EasyOCR,Bizcard is able to extract text from the images.')

with tab2:
  img=st.file_uploader("Upload the image",type=["png","jpg","jpeg"])

  if img is not None:
    st.image(img,width=300)

    text_img,input_img=image_to_text(img)

    text_dict=extracted_text(text_img)

    if text_dict:
      st.success("Text is extracted successfully")

    df=pd.DataFrame(text_dict)
    #st.dataframe(df)

  # converting Image to bytes
    Image_bytes=io.BytesIO()
    input_img.save(Image_bytes,format="PNG")

    image_data=Image_bytes.getvalue()
    #image_data

    #creating dictionary

    data={"IMAGE":[image_data]}
    df_1=pd.DataFrame(data)
    #df_1

    concat_df=pd.concat([df,df_1],axis=1)
    st.dataframe(concat_df)

    button_1=st.button("save",use_container_width=True)
    if button_1:
      mydb=sqlite3.connect("bizcardx.db")
      cursor=mydb.cursor()

      #Table Creation

      create_table_query=''' CREATE TABLE IF NOT EXISTS bizcard_details(name varchar(225),
                                                                  designation varchar(225),
                                                                  company_name varchar(225),
                                                                  contact varchar(225),
                                                                  email varchar(225),
                                                                  website text,
                                                                  address text,
                                                                  pincode varchar(225),
                                                                  image text)'''
      cursor.execute(create_table_query)
      mydb.commit()

      # Insert query
      insert_query='''INSERT INTO bizcard_details(name,designation,company_name,contact,email,website,address,pincode,image)
                                                  values(?,?,?,?,?,?,?,?,?)'''

      datas=concat_df.values.tolist()[0]
      cursor.execute(insert_query,datas)
      mydb.commit()

      st.success("SAVED SUCCESSFULLY")

  #method=st.radio("Select the method",["None","Preview","Modify"])

  tab1,tab2=st.tabs(["Bixcard_Details","Update"])

  #if method=="None":
   # st.write(" ")
  with tab1:
  #if method=="Preview":
    mydb=sqlite3.connect("bizcardx.db")
    cursor=mydb.cursor()

    select_query="SELECT * FROM bizcard_details"

    cursor.execute(select_query)
    table=cursor.fetchall()
    mydb.commit()
    table_df=pd.DataFrame(table, columns=("NAME","DESIGANETION","COMPANY_NAME","CONTACT","EMAIL","WEBSITE","ADDRESS","PINCODE","IMAGE"))

    st.dataframe(table_df)

  #elif method=="Modify" :
  with tab2:
    mydb=sqlite3.connect("bizcardx.db")
    cursor=mydb.cursor()

    select_query="SELECT * FROM bizcard_details"

    cursor.execute(select_query)
    table=cursor.fetchall()
    mydb.commit()
    table_df=pd.DataFrame(table, columns=("NAME","DESIGNATION","COMPANY_NAME","CONTACT","EMAIL","WEBSITE","ADDRESS","PINCODE","IMAGE"))

    col1,col2=st.columns(2)
    with col1:
      selected_name=st.selectbox("Select the NAME",table_df["NAME"])
    df_3=table_df[table_df["NAME"]==selected_name]

    #st.dataframe(df_3)
    df_4=df_3
    #st.dataframe(df_4)
    col1,col2=st.columns(2)
    with col1:

      mod_name=st.text_input("Name",df_3["NAME"].unique()[0])
      mod_designation=st.text_input("Designation",df_3["DESIGNATION"].unique()[0])
      mod_Companyname=st.text_input("Company_Name",df_3["COMPANY_NAME"].unique()[0])
      mod_contact=st.text_input("Contact",df_3["CONTACT"].unique()[0])
      mod_email=st.text_input("Email",df_3["EMAIL"].unique()[0])
      df_4["NAME"]=mod_name
      df_4["DESIGNATION"]=mod_designation
      df_4["COMPANY_NAME"]=mod_Companyname
      df_4["CONTACT"]=mod_contact
      df_4["EMAIL"]=mod_email

    with col2:
      mod_website=st.text_input("Website",df_3["WEBSITE"].unique()[0])
      mod_address=st.text_input("Address",df_3["ADDRESS"].unique()[0])
      mod_pincode=st.text_input("Pincode",df_3["PINCODE"].unique()[0])
      mod_image=st.text_input("Image",df_3["IMAGE"].unique()[0])

      df_4["WEBSITE"]=mod_website
      df_4["ADDRESS"]=mod_address
      df_4["PINCODE"]=mod_pincode
      df_4["IMAGE"]=mod_image

    #st.dataframe(df_4)

    col1,col2=st.columns(2)
    with col1:
      button_3=st.button("Modify",use_container_width=True)

      if button_3:
        mydb=sqlite3.connect("bizcardx.db")
        cursor=mydb.cursor()



        cursor.execute(f" DELETE FROM bizcard_details WHERE NAME= '{selected_name}'")
        create_table_query=''' CREATE TABLE IF NOT EXISTS bizcard_details(name varchar(225),
                                                                  designation varchar(225),
                                                                  company_name varchar(225),
                                                                  contact varchar(225),
                                                                  email varchar(225),
                                                                  website text,
                                                                  address text,
                                                                  pincode varchar(225),
                                                                  image text)'''
        cursor.execute(create_table_query)
        mydb.commit()

        insert_query='''INSERT INTO bizcard_details(name,designation,company_name,contact,email,website,address,pincode,image)
                                                    values(?,?,?,?,?,?,?,?,?)'''

        datas=df_4.values.tolist()[0]
        #st.write(insert_query)
        #st.write(datas)
        cursor.execute(insert_query,datas)

        

        mydb.commit()

        st.success("MODIFIED SUCCESSFULLY")

        st.dataframe(df_4)

#elif select=="Delete":
with tab3:
  mydb=sqlite3.connect("bizcardx.db")
  cursor=mydb.cursor()

  col1,col2=st.columns(2)

  with col1:
    select_query="SELECT NAME  FROM bizcard_details"
    cursor.execute(select_query)
    table1=cursor.fetchall()
    mydb.commit()

    names=[]

    for i in table1:
      names.append(i[0])

    name_select=st.selectbox("Select the name",names)

  with col2:
    select_query="SELECT  DESIGNATION FROM bizcard_details"
    cursor.execute(select_query)
    table2=cursor.fetchall()
    mydb.commit()

    designations=[]

    for j in table2:
      designations.append(j[0])

    designation_select=st.selectbox("Select the Designation",designations)

  if name_select and designation_select:

   col1,col2,col3=st.columns(3)

   with col1:
    st.write(f"Selected Name : {name_select}")
    st.write("")
    st.write("")
    st.write("")
    st.write("")
    st.write(f"Selected Designation : {designation_select}")

   with col2:
    st.write("")
    st.write("")
    st.write("")
    st.write("")
    st.write("")

    remove=st.button("Delete",use_container_width=True)

    if remove:
      cursor.execute(f" DELETE FROM bizcard_details WHERE NAME= '{name_select}' AND DESIGNATION = '{designation_select}' ")
      mydb.commit()

      st.warning("DELETED")

