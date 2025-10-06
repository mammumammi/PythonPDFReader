import os 
from concurrent.futures import ThreadPoolExecutor, as_completed
from sys import exception
from find import push_to_sheet

from backend.find import read_pdf

def process_pdf_batch(folder_path,max_workers):
    pdf_files=[os.path.join(folder_path,f) for f in os.listdir(folder_path) if f.endswith(".pdf")]
    results =[]

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_pdf= {executor.submit(read_pdf,pdf): pdf for pdf in pdf_files}

        for future in as_completed(future_to_pdf):
            pdf = future_to_pdf[future]
            try:
                data = future.result()
                results.append(data)
                print(f"Processed: {pdf}")
            except exception as e:
                print(f"Error processing: {e}")

    return results

if __name__ == "__main__":
    folder = "policies"
    all_data = process_pdf_batch(folder,max_workers=4)
    print("Batch processing done")
    print(all_data)

    for data in all_data:
        push_to_sheet(data)