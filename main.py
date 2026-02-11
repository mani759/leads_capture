from flask import Flask, render_template,request, redirect,session
import uuid
import firebase_admin
from firebase_admin import credentials, firestore, auth
from flask import url_for
import os
import json





firebase_key = json.loads(os.environ["FIREBASE_KEY"])
cred = credentials.Certificate(firebase_key)
firebase_admin.initialize_app(cred)
db = firestore.client()

leads={}
landing_page={}
app=Flask(__name__)
app.secret_key="super-secret-key"
@app.route("/")
def home():
    return render_template("index.html",logged_in=("user_id" in session))


# @app.route("/signup",methods=['GET','POST'])
# def signup():
#     if request.method=="POST":
#         email=request.form["email"]
#         password=request.form["password"]

#         user=auth.create_user(email=email,password=password)

#         session['user_id']=user.uid
#         return redirect("/dashboard")
#     return render_template("signup.html")
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        try:
            user = auth.create_user(email=email, password=password)
            session["user_id"] = user.uid
            return redirect("/")

        except auth.EmailAlreadyExistsError:
            return render_template(
                "signup.html",
                error="Email already exists. Please login."
            )

    return render_template("signup.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]

        user = auth.get_user_by_email(email)
        session["user_id"] = user.uid

        return redirect("/")

    return render_template("login.html")

def login_required():
    return "user_id" in session

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")



# @app.route("/create", methods=['GET','POST'])
# def create():
#     if request.method=='POST':
#         business=request.form['business_name']
#         headline=request.form['headline']
#         cta=request.form['cta']


#         slug=str(uuid.uuid4())[:8]

#         # landing_page[slug]={
#         #     "business":business,
#         #     "headline":headline,
#         #     "cta":cta,
#         # }
#         db.collection("landing_page").document(slug).set({
#     "business": business,
#     "headline": headline,
#     "cta": cta
# })


#         # link=f"/l/{slug}"
#         link = request.host_url.rstrip("/") + url_for("landing", slug=slug)
#         return render_template('success.html',link=link)
#     return render_template("create.html")

@app.route("/create", methods=["GET", "POST"])
def create():
    if "user_id" not in session:
        return redirect("/login")

    if request.method == "POST":
        business = request.form["business_name"]
        headline = request.form["headline"]
        cta = request.form["cta"]

        slug = str(uuid.uuid4())[:8]
        user_id = session["user_id"]

        db.collection("landing_page").document(slug).set({
            "user_id": user_id,   # 🔑 KEY FIX
            "business": business,
            "headline": headline,
            "cta": cta
        })

        link = request.host_url.rstrip("/") + url_for("landing", slug=slug)
        return render_template("success.html", link=link)

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

# @app.route("/submit/<slug>",methods=["GET","POST"])
# def submit(slug):
#     if request.method=="POST":
#         name=request.form['name']
#         email=request.form['email']
#         phone=request.form['phone']

#         if slug not in leads:
#             leads[slug]=[]

#         # leads[slug].append({
#         #     'name':name,
#         #     'email':email,
#         #     'phone':phone,
#         #     'STATUS':"NEW"
#         # })

#         db.collection("leads").add({
#              "slug": slug,
#              "name": name,
#              "email": email,
#              "phone": phone,
#              "status": "New"
# })



#         return render_template("thankyou.html")

@app.route("/submit/<slug>", methods=["POST"])
def submit(slug):
    name = request.form["name"]
    email = request.form["email"]
    phone = request.form["phone"]

    page_doc = db.collection("landing_page").document(slug).get()
    if not page_doc.exists:
        return "Invalid page", 404

    page = page_doc.to_dict()

    db.collection("leads").add({
        "user_id": page["user_id"],  # 🔑 OWNER
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
    if "user_id" not in session:
        return redirect("/login")
        
    user_id=session["user_id"]
    pages = db.collection("landing_page") \
        .where("user_id","==", user_id) \
            .stream()
    dashboard_data = []

    for page in pages:
        page_data = page.to_dict()
        slug = page.id

        leads_query = db.collection("leads") \
            .where("slug", "==", slug) \
                .where("user_id","==",user_id)\
                    .stream()
        page_leads = [lead.to_dict() for lead in leads_query]
        landing_url = request.host_url.rstrip("/") + url_for("landing", slug=slug)

        dashboard_data.append({
    "business": page_data["business"],
    "slug": slug,
    "landing_url": landing_url,
    "leads": page_leads
})

    return render_template("dashboard.html", dashboard_data=dashboard_data)



if __name__=="__main__":
    app.run(debug=True)