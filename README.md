## TeleFramboise

# Motivation
Ayant récemment fait l'acquisition d'un micro-ordinateur **Raspberry Pi 4**, je souhaite le convertir en serveur hébergeant des services comme :
- Messagerie instantanée (comme Dialog ou MAtrix.org)
- NAS
- FTP
- Wifi-AP

Pour gérer ces services, j'aurai besoin d'un accès à distance. Ce pendant, l'utilisation d'un tunnel **SSH** nécessiterait a priori la redirection de ports, ce qui n'est pas forcément possible. Pour pallier à ce problème, une solution est d'utiliser une application de messagerie instantanée, open source et suffisamment sécurisée et pourvue d'un API permettant la mise en place simple d'un bot et de son contrôle par des scripts Python. Mon choix s'est porté sur Telegram, application connue et réputée.

# Implémentation
J'utilise le module Python [Telepot](https://github.com/nickoala/telepot), qui permet de faire la passerelle entre un script Python et l'API de Telegram. J'utilise aussi le module [Wikipedia](https://github.com/goldsmith/Wikipedia) (cf. Fonctionnalités)

Le script s'articule autour de la routine ```telepot.message_loop```, qui permet d'appeler une fonction à chaque message reçu. La fonction est, en l'occurence, la fonction ```handle``` qui, à la réception d'un message, le découpe et tente de reconnaître une commande (les commandes sont toutes de la forme ```/command```, par convention). Lorsqu'une commande est reconnue, sous réserve d'authentification de l'utilisateur et d'autorisation **admin** (cf. Sécurité), la fonction associée est appelée, avec le message découpé passé en argument. 

# Gestion des commandes
Des commandes peuvent être ajoutées au bot en ajoutant tout simplement les fonctions correspondantes au script, précédées du décorateur 

```python 
commandHandler(nom, category = "Default", admin = False)
```

Ce décorateur ajoute les fonctions au dictionnaire des commandes supportées et garde en mémoire leur catégorie (pour un annuaire des commandes plus structuré) et leur nécessité ou non d'une authentification admin.

# Sécurité
Le problème qui se pose est le suivant : les bots Telegram sont publics, ie. il est possible à tout utilisateur de les contacter et de les utiliser, ce qui n'est, dans mon cas, absolument pas souhaitable. Pour cela, j'ai déjà mis en place un système d'authentification rudimentaire, pour m'assurer que nul autre que moi ne puisse utiliser les commandes de mon bot.

Premièrement, chaque message reçu, s'il n'émane pas d'une conversation ayant un certain ```id``` (en pratique l'```id``` associé à ma propre conversation avec le bot), ne peut déclencher de réponse du bot.

De plus, les fonctions sensibles, pouvant affecter le système (comme ```/shutdowm``` ou ```/reboot```) ne peuvent de plus être utilisées que si l'utilisateur a activé le ```mode admin```, avec la commande ```/adminmode mdp``` où mdp est le mot de passe admin éventuellement associé à l'```id``` de la conversation. Ce mot de passe est stocké localement, après avoir été hash par la l'implémentation du module ```hashlib``` de la bibliothèque standard de l'algorithme **sha512**.

Par mesure de sécurité supplémentaire, toutes les 10 minutes, toutes les autorisations ```admin``` sont supprimées.

Néanmoins, le caractère public du bot pose un problème : je n'ai pas encore trovué de moyen d'éviter les attaques de type ```DDoS``` sur le bot, pouvant surcharger la capacité de traitement assez limité du Raspberry.

# Fonctionnalités
Liste des commandes déjà implémentées et leur utilité:
* ```/ping``` : Renvoie ```pong```. Sert à déterminer si le bot fonctionne.
* ```/chat``` : Renvoie ```miaou```. Même utilité que ```/ping```
* ```/help``` : Renvoie la liste des commandes disponibles + docstrings. Ces commandes sont classées par catégorie.
* ```/stats``` : Renvoie des informations de base sur l'état du Raspberry : utilisatio net température du CPU, utilisation de la RAM
* ```/echo msg``` : Renvoie ```msg```
* ```/wikisum -lang key_words``` : Fait une recherche Wikipédie avec comme mots-clés ```key_words``` et si un résultat est trouvé, renvoie une résumé de l'article. L'argument optionnel ```-lang``` sert à forcer l'utilisation d'une langue précisé, spécifiée par son [code](https://meta.wikimedia.org/wiki/List_of_Wikipedias)
* ```/shutdown``` : Envoie dans une console la commande ```sudo shutdown now```. Nécessité l'authentificatio, ```admin```
* ```/restart``` : Envoie dans une console la commande ```sudo restart now```. Nécessité l'authentificatio, ```admin```
