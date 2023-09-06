import psycopg2
import sys
from xml.dom.minidom import *
from sshtunnel import SSHTunnelForwarder

def get_quickcodes(id_shop):
    query = f"""
    SELECT
	pos.t_quickcodes.val, 
	pos.t_quickcodes.description, 
	pos.t_articles_group."name"
FROM
	pos.t_barcode
	INNER JOIN
	pos.t_article
	ON 
		pos.t_barcode.id_article = pos.t_article.id_article AND
		pos.t_barcode.id_shop = pos.t_article.id_shop
	INNER JOIN
	pos.t_articles_group
	ON 
		pos.t_article.id_articles_group = pos.t_articles_group.id_articles_group AND
		pos.t_article.id_shop = pos.t_articles_group.id_shop
	INNER JOIN
	pos.t_quickcodes
	ON 
		pos.t_barcode.barcode = pos.t_quickcodes.val AND
		pos.t_barcode.id_shop = pos.t_quickcodes.id_shop
WHERE
	pos.t_quickcodes.id_shop = {id_shop}  AND "val" NOT LIKE '22%'
ORDER BY "name";
    """

    connect = psycopg2.connect(database="db_server", user="postgres", host='192.168.1.139', port="5432")
    cursor = connect.cursor()
    cursor.execute(query)
    result = cursor.fetchall()
    return result

def make_xml():
    quickcodes = get_quickcodes(597)

    #get distinct groups
    groups = set()
    for q in quickcodes:
        groups.add(q[2])
    groups = list(groups)

    doc = Document()
    node = doc.createElement('root')
    #doc.createTextNode('bar')
    for g in groups:
        group = doc.createElement('group')
        group.setAttribute("text", g)
        for q in quickcodes:
            if q[2] == g:
                good = doc.createElement("good")
                name = doc.createElement("name")
                name.appendChild(doc.createTextNode(q[1]))
                barcode = doc.createElement("barcode")
                barcode.appendChild(doc.createTextNode(q[0]))
                good.appendChild(name)
                good.appendChild(barcode)
                group.appendChild(good)
        node.appendChild(group)

    doc.appendChild(node)
    return doc
if __name__ == '__main__':
    print(make_xml().toxml())
    #make_xml().writexml(sys.stdout)