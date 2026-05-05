from conexion import *
import pytest   

class Test_autores:

    def setup_class(self):
        # Preparación del entorno de las pruebas
        self.url = "http://localhost:5087/autores"
        idAutor = "A01"
        nom = "Gabriel García Márquez"
        email = "gabriel.garcia@márquez.com"
        idPais = "MX"
        sql = f"INSERT INTO autores (idAutor,nombre,email,idPais) VALUES ('{idAutor}','{nom}','{email}','{idPais}')"
        mi_cursor.execute(sql)
        mi_db.commit()

    def test_lista_autores(self):
        esperado = "autores"
        # Ejecutar la prueba
        calculado = requests.get(self.url)
        # Verificación
        assert calculado.status_code == 200
        assert calculado.json()["mensaje"]==esperado

    @pytest.mark.parametrize(
        ["nuevo_entrada","esperado_entrada"],
        [({"idAutor":"A02","nombre":"Autor de Prueba","email":"prueba@example.com","idPais":"MX"},"Autor agregado con éxito"),  
         ({"idAutor":"A01","nombre":"Gabriel García Márquez","email":"gabriel.garcia@márquez.com","idPais":"PR"},"Id de autor ya existe")]
    )
    def test_agregar(self,nuevo_entrada,esperado_entrada):
        # Ejecutar la prueba
        calculado = requests.post(self.url,json=nuevo_entrada)
        # Verificar la prueba
        assert calculado.status_code == 200
        assert esperado_entrada == calculado.json()["mensaje"]

    @pytest.mark.parametrize(
        ["id_entrada","esperado_entrada"], 
        [("A01","Autor encontrado"),
         ("A09","Id no encontrado")]
    )
    def test_busqueda(self,id_entrada,esperado_entrada):
        idAutor = id_entrada
        esperado = esperado_entrada
        # Ejecutar la prueba
        calculado = requests.get(f"{self.url}/{idAutor}")
        # Verificar la prueba
        assert calculado.status_code == 200
        assert esperado == calculado.json()["mensaje"]
    
    #Para cuando el autor existe y se modifica con éxito
    def test_modifica1(self):
        idAutor = "A01"
        nombre = "Gabriel García Márquez Modificado"
        email = "gabriel.garcia.modificado@márquez.com"
        idPais = "MX"
        nuevo = {"idAutor":idAutor,"nombre":nombre,"email":email,"idPais":idPais}
        esperado = "Autor modificado con éxito"
        # Ejecutar la prueba
        calculado = requests.put(f"{self.url}/{idAutor}",json=nuevo)
        # Verificar la prueba
        assert calculado.status_code == 200
        assert esperado == calculado.json()["mensaje"]

        sql = f"SELECT * FROM autores WHERE idAutor='{idAutor}'"
        mi_cursor.execute(sql)
        datos = mi_cursor.fetchall()[0]
        assert nombre==datos[1] and email==datos[2] and idPais==datos[3]

    # Para cuando el país no existe y se intenta modificar
    def test_modifica2(self):
        idAutor = "A08"
        nombre = "Autor de Prueba Modificado"
        email = "prueba.modificada@example.com"
        idPais = "PR"
        nuevo = {"idAutor":idAutor,"nombre":nombre,"email":email,"idPais":idPais}
        esperado = "Autor no existe"
        # Ejecutar la prueba
        calculado = requests.put(f"{self.url}/{idAutor}",json=nuevo)
        # Verificar la prueba
        assert calculado.status_code == 200
        assert esperado == calculado.json()["mensaje"]
        
    @pytest.mark.parametrize(
        ["id_entrada","esperado_entrada"],
        [("A01","Autor eliminado con éxito!"),
         ("A09","Autor no existe")]
    )
    def test_elimina(self,id_entrada,esperado_entrada):
        idAutor = id_entrada
        esperado = esperado_entrada
        # Ejecutar la prueba
        calculado = requests.delete(f"{self.url}/{idAutor}")
        # Verificar la prueba
        assert calculado.status_code == 200
        assert esperado == calculado.json()["mensaje"]

        sql = f"SELECT * FROM autores WHERE idAutor='{idAutor}'"
        mi_db.commit()
        mi_cursor.execute(sql)
        datos = mi_cursor.fetchall()
        assert len(datos)==0
   
def teardown_class(self):
        # Limpia la base de datos
        sql = f"DELETE FROM autores WHERE idAutor='A01'"
        mi_cursor.execute(sql)
        mi_db.commit()