from flask import Flask, render_template, request, send_from_directory, jsonify
from datetime import datetime
import profile
import moves
import os
import news
import pandas as pd
import csv

#ngrok launch code in terminal after running: ngrok http 127.0.0.1:5000
app = Flask(__name__)

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/profile")
def profiles():
    return render_template("profiles.html")

@app.route("/home")
def home_page():
    return render_template("home.html")

### NEWS PAGE ###
@app.route("/news")
def news_page():
    today = datetime.now().strftime("%Y-%m-%d")
    data_directory = os.path.join(os.getcwd(), "data")
    world_filename = f"APAC_World_News_{today}.xlsx"
    market_filename = f"APAC_Market_News_{today}.xlsx"
    world_filepath = os.path.join(data_directory, world_filename)
    market_filepath = os.path.join(data_directory, market_filename)

    # Check if today's world news file already exists
    if os.path.exists(world_filepath):
        try:
            world_news_df = pd.read_excel(world_filepath)
            world_news = world_news_df.to_dict('records')
        except Exception as e:
            return str(e)
    else:
        try:
            nytatoday = news.news_nyta("https://www.nytimes.com/international/section/world/asia")
            etiatoday = news.news_etia("https://economictimes.indiatimes.com/topic/asia-pacific")
            world_news = nytatoday + etiatoday
            moves.moves_to_excel(world_news, world_filename)
        except Exception as e:
            return str(e)

    # Check if today's market news file already exists
    if os.path.exists(market_filepath):
        try:
            market_news_df = pd.read_excel(market_filepath)
            market_news = market_news_df.to_dict('records')
        except Exception as e:
            return str(e)
    else:
        try:
            fx = news.news_fx("https://www.fx-markets.com/regions/asia")
            etimtoday = news.news_etim('https://economictimes.indiatimes.com/topic/asia-pacific-market')
            market_news = fx + etimtoday
            moves.moves_to_excel(market_news, market_filename)
        except Exception as e:
            return str(e)

    return render_template("news.html", world_news=world_news, market_news=market_news,
                           filename_world=world_filename, filename_market=market_filename)

@app.route("/news/world", methods=["GET","POST"])
def world_news_all():
    today = datetime.now().strftime("%Y-%m-%d")
    world_filename = f"APAC_World_News_{today}.xlsx"
    data_directory = os.path.join(os.getcwd(), "data")
    world_filepath = os.path.join(data_directory, world_filename)

    try:
        world_news_df = pd.read_excel(world_filepath)
        world_news = world_news_df.to_dict('records')
        return render_template("world_news.html", world_news=world_news)
    except Exception as e:
        return str(e)

@app.route("/news/market", methods=["GET","POST"])
def market_news_all():
    today = datetime.now().strftime("%Y-%m-%d")
    market_filename = f"APAC_Market_News_{today}.xlsx"
    data_directory = os.path.join(os.getcwd(), "data")
    market_filepath = os.path.join(data_directory, market_filename)

    try:
        market_news_df = pd.read_excel(market_filepath)
        market_news = market_news_df.to_dict('records')
        return render_template("market_news.html", market_news=market_news)
    except Exception as e:
        return str(e)

### MOVES NEWS PAGE ###
@app.route("/moves", methods=["GET", "POST"])
def moves_page():
    today = datetime.now().strftime("%Y-%m-%d")
    filename = f"Moves_News_{today}.xlsx"
    data_directory = os.path.join(os.getcwd(), "data")
    filepath = os.path.join(data_directory, filename)

    # Check if today's file already exists
    if os.path.exists(filepath):
        try:
            move_news_df = pd.read_excel(filepath)
            move_news = move_news_df.to_dict('records')
        except Exception as e:
            return str(e)
    else:
        try:
            base_url = "https://fundselectorasia.com/people-moves/"
            html_content = moves.fetch_html(base_url)
            profiles = moves.parse_html(html_content)
            if profiles:
                profiles = profiles[:-1]  # Remove the last item from the list before exporting
                filepath = moves.moves_to_excel(profiles, filename)
                move_news_df = pd.read_excel(filepath)
                move_news = move_news_df.to_dict('records')
            else:
                return "No new data to scrape."
        except Exception as e:
            return str(e)

    return render_template("moves.html", move_news=move_news, filename=filename)

@app.route("/news/moves", methods=["GET","POST"])
def moves_news_all():
    today = datetime.now().strftime("%Y-%m-%d")
    moves_filename = f"Moves_News_{today}.xlsx"
    data_directory = os.path.join(os.getcwd(), "data")
    moves_filepath = os.path.join(data_directory, moves_filename)

    try:
        moves_news_df = pd.read_excel(moves_filepath)
        move_news = moves_news_df.to_dict('records')
        return render_template("moves_news.html", move_news=move_news)
    except Exception as e:
        return str(e)


### CHARTS PAGE ###
@app.route("/charts")
def charts_page():
    return render_template("charts.html")

@app.route('/api/data', methods=['GET'])
def fetch_csv_data():
    try:
        file_path = os.path.join('org_data', 'citiemployees.csv')
        with open(file_path, 'r') as file:
            csv_reader = csv.reader(file)
            data = [row for row in csv_reader]
        return jsonify(data)
    except Exception as e:
        return str(e), 500

@app.route('/api/data', methods=['POST'])
def save_csv_data():
    try:
        nodes = request.json.get('data')
        file_path = os.path.join('org_data', 'citiemployees.csv')
        with open(file_path, 'r') as file:
            csv_reader = csv.reader(file)
            header = next(csv_reader)  # Skip header
            existing_data = list(csv_reader)

        for node in nodes:
            node_id = str(node['id'])
            for row in existing_data:
                if row[0] == node_id:
                    row[1] = str(node['pid'])
                    row[2] = node['name']
                    row[3] = node['title']
                    row[4] = node.get('department', '')  # Update department if exists

        with open(file_path, 'w', newline='') as file:
            csv_writer = csv.writer(file)
            csv_writer.writerow(header)
            csv_writer.writerows(existing_data)

        return 'Data saved successfully', 200
    except Exception as e:
        return str(e), 500

### PROFILE PAGE ###
@app.route("/search", methods=["GET", "POST"])
def search():
    if request.method == "GET":
        role = request.args.get("role")
        bank = request.args.get("bank")
        department = request.args.get("department")
        region = request.args.get("region")

        # Create a keyword from the query parameters
        keyword = f"{role} {bank} {department} {region}".strip()
        today = datetime.now().strftime("%Y-%m-%d")
        profile_data_directory = os.path.join(os.getcwd(), "profile_data")
        filename = f"{keyword.replace(' ', '_')}_{today}_profiles.xlsx"
        filepath = os.path.join(profile_data_directory, filename)

        # Check if the Excel file for the current search query exists
        if os.path.exists(filepath) and keyword:
            try:
                profiles_df = pd.read_excel(filepath)
                profiles = profiles_df.to_dict('records')
            except Exception as e:
                return str(e)
        elif keyword:
            try:
                browser = profile.initialize_browser()
                search1 = profile.scrape_multiple_profiles(browser, role, department, bank, region)
                search2 = profile.scrape_multiple_profiles2(browser, role, department, bank, region)
                profiles = search1 + search2
                profile.profiles_to_excel(profiles, filename)
                browser.quit()

            except Exception as e:
                return str(e)
        else:
            return render_template("search.html")

        return render_template("search.html", profiles=profiles, keyword=keyword, filename=filename)


### EDITS PAGE ###
def load_data(file_path):
    """Load individual Excel file into DataFrame, ensuring necessary columns are present."""
    try:
        df = pd.read_excel(file_path, engine='openpyxl')
        # Make sure that all expected columns are strings, replace NaN with suitable defaults
        df.fillna({
            'URL': 'Not Specified',
            'Name': 'Not Specified',
            'Position': 'Not Specified',
            'Company': 'Not Specified',
            'Location': 'Not Specified',
            'Periods': 'Not Specified',
            'Department': 'Not Specified',
        }, inplace=True)
        return df
    except Exception as e:
        print(f"Failed to load {file_path}: {str(e)}")
        return pd.DataFrame()

def load_all_data(directory):
    """Loads all Excel files from a directory into a single DataFrame."""
    all_data = pd.DataFrame()
    for filename in os.listdir(directory):
        if filename.endswith(".xlsx"):
            file_path = os.path.join(directory, filename)
            df = load_data(file_path)
            df['source_file'] = filename  # Track the source file
            all_data = pd.concat([all_data, df], ignore_index=True)
    return all_data

def merge_similar_profiles(all_data):
    """Merge profiles based on first name, last name, and company similarity."""
    def extract_name_parts(name):
        parts = name.split()
        return parts[0], parts[-1] if len(parts) > 1 else parts[0]

    # Ensure that all columns are strings and handle NaN values appropriately
    all_data.fillna('', inplace=True)  # Replace NaN with empty strings for safe string operations
    all_data['URL'] = all_data['URL'].astype(str)
    all_data['Position'] = all_data['Position'].astype(str)
    all_data['Location'] = all_data['Location'].astype(str)
    all_data['Periods'] = all_data['Periods'].astype(str)
    all_data['Department'] = all_data['Department'].astype(str)

    all_data['First Name'], all_data['Last Name'] = zip(*all_data['Name'].map(extract_name_parts))
    all_data['Base Company'] = all_data['Company'].apply(lambda x: x.split()[0].lower())

    merged_entries = []
    grouped = all_data.groupby(['First Name', 'Last Name', 'Base Company'])

    for _, group in grouped:
        entry = {
            'URL': ', '.join(group['URL'].unique()),
            'Name': group.iloc[0]['Name'],
            'Position': ', '.join(filter(None, group['Position'].unique())),  # Filter out empty strings
            'Company': group.iloc[0]['Company'],
            'Location': ', '.join(filter(None, group['Location'].unique())),  # Filter out empty strings
            'Periods': ', '.join(filter(None, group['Periods'].unique())),  # Filter out empty strings
            'Department': ', '.join(filter(None, group['Department'].unique()))  # Filter out empty strings
        }
        merged_entries.append(entry)

    return pd.DataFrame(merged_entries)

def save_merged_data(merged_data, directory):
    """Save the merged data to a new file and clear old files, except the new one."""
    new_file_path = os.path.join(directory, 'MergedData.xlsx')
    merged_data.to_excel(new_file_path, index=False)
    for filename in os.listdir(directory):
        if filename != 'MergedData.xlsx':
            os.remove(os.path.join(directory, filename))

@app.route('/edits', methods=["GET", "POST"])
def edits_page():
    if request.method == "POST":
        name = request.form.get('name')
        position = request.form.get('position')
        bank = request.form.get('bank')
        location = request.form.get('location')

        directory = "profile_data"
        all_data = load_all_data(directory)
        merged_data = merge_similar_profiles(all_data)
        save_merged_data(merged_data, directory)  # Save the merged data and clean the directory

        # Filter the data based on form inputs
        if name:
            merged_data = merged_data[merged_data['Name'].str.contains(name, case=False, na=False)]
        if position:
            merged_data = merged_data[merged_data['Position'].str.contains(position, case=False, na=False)]
        if bank:
            merged_data = merged_data[merged_data['Company'].str.contains(bank, case=False, na=False)]
        if location:
            merged_data = merged_data[merged_data['Location'].str.contains(location, case=False, na=False)]

        entries = merged_data.to_dict('records')
        return render_template("edits.html", entries=entries)
    return render_template("edits.html", entries=[])

@app.route('/delete-entry', methods=['POST'])
def delete_entry():
    name = request.form.get('name')
    position = request.form.get('position')
    company = request.form.get('company')
    location = request.form.get('location')
    periods = request.form.get('periods')
    department = request.form.get('department')

    directory = "profile_data"
    filepath = os.path.join(directory, "MergedData.xlsx")

    try:
        df = pd.read_excel(filepath)

        # Create a condition for deletion
        condition = (
            (df['Name'] == name) &
            (df['Position'] == position) &
            (df['Company'] == company) &
            (df['Location'] == location) &
            (df['Periods'] == periods) &
            (df['Department'] == department)

        )

        # Check if there are matching records
        if not df[condition].empty:
            df = df[~condition]  # Keep rows where condition is not met
            df.to_excel(filepath, index=False)
            return jsonify({'message': 'Deleted successfully'}), 200
        else:
            return jsonify({'error': 'No matching record found for deletion'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/get-entry', methods=['POST'])
def get_entry():
    """ Fetch entry details for editing. """
    name = request.form.get('name')
    position = request.form.get('position')
    company = request.form.get('company')
    location = request.form.get('location')
    periods = request.form.get('periods')
    department = request.form.get('department')
    source_file = request.form.get('source_file')

    directory = "profile_data"
    filepath = os.path.join(directory, source_file)
    df = pd.read_excel(filepath)

    # Find the entry using details provided
    condition = (
        (df['Name'] == name) &
        (df['Position'] == position) &
        (df['Company'] == company) &
        (df['Location'] == location) &
        (df['Periods'] == periods) &
        (df['Department'] == department)
    )
    if df[condition].empty:
        return jsonify({'error': 'Entry not found'}), 404

    entry = df[condition].iloc[0].to_dict()
    return jsonify(entry)

@app.route('/update-entry', methods=['POST'])
def update_entry():
    name = request.form.get('name')
    position = request.form.get('position')
    company = request.form.get('company')
    location = request.form.get('location')
    periods = request.form.get('periods')
    department = request.form.get('department')
    old_name = request.form.get('old_name')  # Assuming old_name is used to locate the original entry

    directory = "profile_data"
    filepath = os.path.join(directory, "MergedData.xlsx")

    try:
        df = pd.read_excel(filepath)
        # Create a condition based on the old name
        condition = (df['Name'] == old_name)

        if df[condition].empty:
            return jsonify({'error': 'No unique record found for update'}), 404

        # Update the entry
        df.loc[condition, 'Name'] = name
        df.loc[condition, 'Position'] = position
        df.loc[condition, 'Company'] = company
        df.loc[condition, 'Location'] = location
        df.loc[condition, 'Periods'] = periods
        df.loc[condition, 'Department'] = department
        df.to_excel(filepath, index=False)
        return jsonify({'message': 'Data updated successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/add-entry', methods=['POST'])
def add_entry():
    name = request.form.get('name')
    position = request.form.get('position')
    company = request.form.get('company')
    location = request.form.get('location')
    periods = request.form.get('periods')
    department = request.form.get('department')

    # Ensure all required fields are provided
    if not all([name, position, company, location, periods, department]):
        return jsonify({'error': 'All fields are required'}), 400

    directory = "profile_data"
    filepath = os.path.join(directory, "Additional_Entries.xlsx")

    try:
        if os.path.exists(filepath):
            df = pd.read_excel(filepath)
        else:
            df = pd.DataFrame(columns=['Name', 'Position', 'Company', 'Location', 'Periods', 'Department'])

        # Create a new DataFrame for the new entry
        new_entry = pd.DataFrame([[name, position, company, location, periods, department]], columns=['Name', 'Position', 'Company', 'Location', 'Periods', 'Department'])
        df = pd.concat([df, new_entry], ignore_index=True)
        df.to_excel(filepath, index=False)
        return jsonify({'message': 'New data added successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(directory=os.getcwd(), path=filename, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
