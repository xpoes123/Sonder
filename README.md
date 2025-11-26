# Sonder 🎵❤️

**Sonder** was an experimental music‑driven dating‑profile and song‑recommendation project.  
Users browsed “dating profiles” generated from songs, swiped right or left, and the system inferred
musical‑taste attributes from these swipes. A native clustering‑based recommendation algorithm then suggested new songs aligned to the user’s evolving profile.

> **⚠️ Deprecated:** This project is archived and no longer functional due to changes in Spotify’s API that removed or restricted the data access the system relied upon.

---

## 💡 Project Overview

Sonder explored a playful question:  
**What if songs had dating profiles—and what if your taste could be inferred by swiping on them?**

The application generated a personality‑style profile for each track using metadata and descriptive features.  
Users would swipe *right* (like) or *left* (dislike) on these profiles.  
Each action updated a set of internal attributes describing the user’s preferences.

Those attributes powered a clustering‑based recommendation engine that surfaced new tracks the user was likely to enjoy.

---

## 🎧 Core Ideas

- **Song Dating Profiles**  
  Each song was assigned a personality‑style description generated from its musical features.

- **Swipe‑Based Preference Modeling**  
  Users interacted with songs through a simple familiar interface, making the experience intuitive and game‑like.

- **Attribute‑Driven User Profiles**  
  Every swipe updated a music‑taste vector representing the user.

- **Clustering‑Based Recommendations**  
  A lightweight machine‑learning approach grouped similar songs and used proximity to recommend music.

---

## 🛑 Deprecation Notice

Sonder relied on Spotify’s Web API for essential metadata.  
Recent changes—including more restrictive access policies, removed fields, and increased authentication requirements—broke the original data pipeline.

As a result:

- Song metadata cannot be fetched consistently  
- Recommendation inputs fail to compute  
- OAuth flows may no longer function  
- The app cannot operate as intended  

Because the project was a personal prototype, it is no longer maintained and is provided **as is**.

---

## 🔄 Future Revival Ideas

If you wish to revive or extend Sonder, possible directions include:

- Integrating with an alternative open music dataset (e.g., MusicBrainz + AcousticBrainz)
- Using embeddings (e.g., Spotify Annoy index dumps, if available externally)
- Expanding the concept to **movies**, **podcasts**, or **books**
- Rebuilding the recommender using modern vector search (FAISS, Milvus, Pinecone)
- Redesigning the swipe‑based interface into a general “taste‑discovery” tool

---

## 📄 License

No license was originally specified.  
If this project is revived, you may add one (MIT recommended for open projects).

---

## 🙏 Acknowledgments

Thanks to Spotify’s API ecosystem for originally making projects like this possible.  
Though the app is deprecated, it remains a fun exploration of **music**, **machine learning**, and **interaction design**.

---

*Repository maintained by @xpoes123. Project archived.*
