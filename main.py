from flask import Flask, render_template,request
import uuid
import firebase_admin
from firebase_admin import credentials, firestore
from flask import url_for, request





cred = credentials.Certificate("firebase_key.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

leads={}
landing_page={}
app=Flask(__name__)
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/create", methods=['GET','POST'])
def create():
    if request.method=='POST':
        business=request.form['business_name']
        headline=request.form['headline']
        cta=request.form['cta']


        slug=str(uuid.uuid4())[:8]

        # landing_page[slug]={
        #     "business":business,
        #     "headline":headline,
        #     "cta":cta,
        # }
        db.collection("landing_page").document(slug).set({
    "business": business,
    "headline": headline,
    "cta": cta
})


        # link=f"/l/{slug}"
        link = request.host_url.rstrip("/") + url_for("landing", slug=slug)
        return render_template('success.html',link=link)
    return render_template("create.html")


@app.route("/l/<slug>")
def landing(slug):
    # data=landing_page.get(slug)
    doc = db.collection("landing_page").document(slug).get()

    # if not data:
    #     return "page not found"
    if not doc.exists:
        return "Page not found", 404
    
    data = doc.to_dict()
    
    return render_template("landing.html", data=data,slug=slug)

@app.route("/submit/<slug>",methods=["GET","POST"])
def submit(slug):
    if request.method=="POST":
        name=request.form['name']
        email=request.form['email']
        phone=request.form['phone']

        if slug not in leads:
            leads[slug]=[]

        # leads[slug].append({
        #     'name':name,
        #     'email':email,
        #     'phone':phone,
        #     'STATUS':"NEW"
        # })

        db.collection("leads").add({
             "slug": slug,
             "name": name,
             "email": email,
             "phone": phone,
             "status": "New"
})



        return render_template("thankyou.html")
    

# @app.route("/dashboard")
# def dashboard():
#     dashboard_data = []

#     for slug, page in landing_page.items():
#         dashboard_data.append({
#             "business": page["business"],
#             "leads": leads.get(slug, [])
#         })

#     return render_template("dashboard.html", dashboard_data=dashboard_data)

@app.route("/dashboard")
def dashboard():
    pages = db.collection("landing_page").stream()
    dashboard_data = []

    for page in pages:
        page_data = page.to_dict()
        slug = page.id

        leads_query = db.collection("leads").where("slug", "==", slug).stream()
        page_leads = [lead.to_dict() for lead in leads_query]

        dashboard_data.append({
            "business": page_data["business"],
            "leads": page_leads
        })

    return render_template("dashboard.html", dashboard_data=dashboard_data)



if __name__=="__main__":
    app.run(debug=True)