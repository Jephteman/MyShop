## Guide d'utilisation

### Interface Utilisateur
_________________________
L'interface graphique est super intuitif 

Tout commence par la page de connection où vous devez remplir le nom d'utilisateur et le mot de passe. <br>
Par defaut, il s'agit de : <br>

   - Nom d'utilisateur : MyShop

   - Mot de passe : MyShop 
<center>
    ![client image 1](img/client_login.PNG)
</center>

Après vous etre bien identifier avec des identifiants valides vous serait alors diriger vers cette page
<center>
    ![client image home](img/home.PNG)
</center>


### Serveur (API)
_________________
## Description Générale
Ce fichier est le point d'entrée pour la partie serveur de l'application. Il utilise le framework Flask pour fournir une API REST permettant de gérer les utilisateurs, les ressources, et les configurations. Le serveur interagit avec une base de données et utilise des cookies pour authentifier les utilisateurs.

---

## Points de Terminaison de l'API

### **Gestion des Utilisateurs**
- **`GET /api/v1/check_cookie`**
    - Vérifie si un utilisateur est connecté via les cookies.
    - **Réponse** : Statut de la connexion.

- **`POST /api/v1/login`**
    - Authentifie un utilisateur avec ses informations de connexion.
    - **Données attendues** : `username`, `password`.
    - **Réponse** : Résultat de l'authentification.

- **`POST /api/v1/reset_passwd`**
    - Réinitialise le mot de passe d'un utilisateur.
    - **Données attendues** : `username`, `password`, `password_confirmation`.

### **Gestion des Ressources** 

En ce qui concerne la gestion des ressources

- **`POST /api/v1/<ressource>/add`**
    - Ajoute une nouvelle entrée dans une ressource (ex. : `users`, `produits`).
    - **Données attendues** : Objet JSON contenant les informations de la ressource.

- **`GET /api/v1/<ressource>/all`**
    - Liste tous les éléments d'une ressource.
    - **Réponse** : Liste des éléments.

- **`GET /api/v1/<ressource>/<id>`**
    - Récupère un élément spécifique d'une ressource.
    - **Paramètre attendu dans l'URL** : `id`.

- **`POST /api/v1/<ressource>/<id>/change`**
    - Modifie un élément spécifique d'une ressource.
    - **Données attendues** : Objet JSON contenant les nouvelles informations.

- **`GET /api/v1/<ressource>/<id>/delete`**
    - Supprime un élément spécifique d'une ressource.
    - **Paramètre attendu dans l'URL** : `id`.

---
