from conexion import *
import pytest   

class Test_editoriales:

    def setup_class(self):
        # Preparación del entorno de las pruebas
        self.url = "http://localhost:5088/editoriales"
        idEditorial = "e01"
        nombre = "Editorial Norma"
        idPais = "PR"
        sql = f"INSERT INTO editoriales (idEditorial,nombre,idPais) VALUES ('{idEditorial}','{nombre}','{idPais}')"
        mi_cursor.execute(sql)
        mi_db.commit()

    def teardown_class(self):
        # Limpia la base de datos
        sql = f"DELETE FROM editoriales WHERE idEditorial='e01'"
        mi_cursor.execute(sql)
        mi_db.commit()

    def test_lista_editoriales(self):
        esperado = "editoriales"
        # Ejecutar la prueba
        calculado = requests.get(self.url)
        # Verificación
        assert calculado.status_code == 200
        assert calculado.json()["mensaje"]==esperado

    @pytest.mark.parametrize(
        ["nuevo_entrada","esperado_entrada"],
        [({"idEditorial":"e02","nombre":"Editorial Prueba","idPais":"MX"},"Editorial agregada con éxito"),  
         ({"idEditorial":"e01","nombre":"Editorial Norma","idPais":"PR"},"Id de editorial ya existe")]
    )
    def test_agregar(self,nuevo_entrada,esperado_entrada):
        idEditorial = nuevo_entrada["idEditorial"]
        nombre = nuevo_entrada["nombre"]
        idPais = nuevo_entrada["idPais"]
        # Ejecutar la prueba
        calculado = requests.post(self.url,json=nuevo_entrada)
        # Verificar la prueba
        assert calculado.status_code == 200
        assert esperado_entrada == calculado.json()["mensaje"]

    @pytest.mark.parametrize(
        ["id_entrada","esperado_entrada"], 
        [("e01","Editorial encontrado"),
         ("e09","Id no encontrado")]
    )
    def test_busqueda(self,id_entrada,esperado_entrada):
        idEditorial = id_entrada
        esperado = esperado_entrada
        # Ejecutar la prueba
        calculado = requests.get(f"{self.url}/{idEditorial}")
        # Verificar la prueba
        assert calculado.status_code == 200
        assert esperado == calculado.json()["mensaje"]
    
    #Para cuando el pais existe y se modifica con éxito
    def test_modifica1(self):
        idEditorial = "e01"
        nombre = "Editorial Norma Modificada"
        idPais = "PR"
        nuevo = {"idEditorial":idEditorial,"nombre":nombre,"idPais":idPais}
        esperado = "Editorial modificado con éxito"
        # Ejecutar la prueba
        calculado = requests.put(f"{self.url}/{idEditorial}",json=nuevo)
        # Verificar la prueba
        assert calculado.status_code == 200
        assert esperado == calculado.json()["mensaje"]

        sql = f"SELECT * FROM editoriales WHERE idEditorial='{idEditorial}'"
        mi_cursor.execute(sql)
        datos = mi_cursor.fetchall()[0]
        assert nombre==datos[1] and idPais==datos[2]

    # Para cuando el editorial no existe y se intenta modificar
    def test_modifica2(self):
        idEditorial = "e09"
        nombre = "Editorial de Prueba Modificada"
        idPais = "PR"
        nuevo = {"idEditorial":idEditorial,"nombre":nombre,"idPais":idPais}
        esperado = "Editorial no existe"
        # Ejecutar la prueba
        calculado = requests.put(f"{self.url}/{idEditorial}",json=nuevo)
        # Verificar la prueba
        assert calculado.status_code == 200
        assert esperado == calculado.json()["mensaje"]
        
    @pytest.mark.parametrize(
        ["id_entrada","esperado_entrada"],
        [("e01","Editorial eliminada con éxito!"),
         ("e09","Editorial no existe")]
    )
    def test_elimina(self,id_entrada,esperado_entrada):
        idEditorial = id_entrada
        esperado = esperado_entrada
        # Ejecutar la prueba
        calculado = requests.delete(f"{self.url}/{idEditorial}")
        # Verificar la prueba
        assert calculado.status_code == 200
        assert esperado == calculado.json()["mensaje"]

        sql = f"SELECT * FROM editoriales WHERE idEditorial='{idEditorial}'"
        mi_cursor.execute(sql)
        datos = mi_cursor.fetchall()
        mi_db.commit()
        assert len(datos)==0