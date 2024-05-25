import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
from BFB_CCC_logic import main as BFB_logic_main
import base64
import time

REQUIRED_COLUMNS = [
    'Product Name', 'Brand Name', 'Price', 'Quantity/Size', 'Shade/Color', 
    'Ingredients', 'Product Type', 'Usage Instructions', 'Expiration Date', 
    'Manufacturing Date', 'Country of Origin', 'Special Features', 
    'Certifications', 'Description', 'Image Path', 'Benefits', 
    'Skin Type Compatibility', 'Packaging', 'Product Images', 'Return Policy', 
    'Disclaimer'
]

def read_product_data(uploaded_file):
    try:
        df = pd.read_csv(uploaded_file)
        st.write("CSV Uploaded Successfully")
        return df
    except Exception as e:
        st.error(f"Error reading file: {e}")
        return pd.DataFrame()

def check_columns(df):
    return [col for col in REQUIRED_COLUMNS if col not in df.columns]

def plot_metrics(metrics_df):
    metrics = ['Correctness', 'Compliance', 'Completeness']
    scores = metrics_df[metrics].mean()

    fig, ax = plt.subplots()
    scores.plot(kind='bar', ax=ax)
    ax.set_ylabel('Score')
    ax.set_title('Overall Metrics')
    return fig

def plot_processing_times(processing_times):
    fig, ax = plt.subplots()
    ax.plot(processing_times, marker='o')
    ax.set_ylabel('Processing Time (s)')
    ax.set_title('Processing Time per Data Entry')
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    return fig

def print_falling_short_instances(metrics_df):
    falling_short_df = metrics_df[(metrics_df['Correctness'] < 10) |    
                                  (metrics_df['Compliance'] < 10) | 
                                  (metrics_df['Completeness'] < 10)]
    
    if not falling_short_df.empty:
        st.write("Instances where metrics fall short:")
        st.write(falling_short_df)

# def process_image(image_path):
#     try:
#         image = cv2.imread(image_path)
#         if image is None:
#             raise ValueError(f"Image at {image_path} could not be read.")
#         # Resize or process the image as required
#         resized_image = cv2.resize(image, (100, 100))
#         return resized_image
#     except Exception as e:
#         st.error(f"Error processing image {image_path}: {e}")
#         return None

def main():
    st.title("Score Your Catalogue:")
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

    if uploaded_file:
        prod_data_df = read_product_data(uploaded_file)
        missing_columns = check_columns(prod_data_df)

        if missing_columns:
            st.error(f"Missing columns: {', '.join(missing_columns)}")
        else:
            # Initialize an empty list to store processing times
            processing_times = []

            # Process each row and track the time taken
            res_scores = pd.DataFrame()
            for index, row in prod_data_df.iterrows():
                start_time = time.time()
                
                # # Process the image if the path is provided
                # image_path = row['Image Path']
                # if pd.notna(image_path):
                #     process_image(image_path)
                
                try:
                    result = BFB_logic_main(pd.DataFrame([row]))
                    res_scores = pd.concat([res_scores, result], ignore_index=True)
                except Exception as e:
                    st.error(f"Error processing row {index}: {e}")
                    continue
                
                end_time = time.time()
                processing_times.append(end_time - start_time)

            st.write(res_scores.head())

            # Plot metrics and processing times side by side
            col1, col2 = st.columns(2)

            with col1:
                st.header("Overall Metrics")
                fig1 = plot_metrics(res_scores)
                st.pyplot(fig1)

            with col2:
                st.header("Processing Times")
                fig2 = plot_processing_times(processing_times)
                st.pyplot(fig2)

            # Print instances where metrics fall short
            print_falling_short_instances(res_scores)

            # Allow users to download the results
            csv = res_scores.to_csv(index=False)
            b64 = base64.b64encode(csv.encode()).decode()
            href = f'<a href="data:file/csv;base64,{b64}" download="data.csv">Download results</a>'
            st.markdown(href, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
