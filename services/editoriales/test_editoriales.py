from conexion import *
import pytest   

class Test_editoriales:

    def setup_class(self):
        # Preparación del entorno de las pruebas
        self.url = "http://localhost:5088/editoriales"
        self.url_paises = "http://localhost:5089/paises"
        idEditorial = "e01"
        nombre = "Editorial Norma"
        idPais = "PR"

        # ── Verificar si "PR" existe usando el endpoint de paises ──
        respuesta = requests.get(f"{self.url_paises}/{idPais}")
        if respuesta.json()["mensaje"] == "Id no encontrado":
            # Si no existe, lo inserta usando el endpoint POST de paises
            requests.post(self.url_paises, json={
                "idPais": idPais,
                "nombre": "Puerto Rico",
                "continente": "América"
            })

        # ── Verificar si "MX" existe (se usa en test_agregar) ──
        respuesta_mx = requests.get(f"{self.url_paises}/MX")
        if respuesta_mx.json()["mensaje"] == "Id no encontrado":
            requests.post(self.url_paises, json={
                "idPais": "MX",
                "nombre": "Mexico",
                "continente": "América"
            })

        # ── Limpiar editoriales de prueba por si quedaron de ejecuciones anteriores ──
        mi_cursor.execute("DELETE FROM editoriales WHERE idEditorial IN ('e01','e02')")
        mi_db.commit()

        # ── Insertar la editorial base para los tests ──
        sql = f"INSERT INTO editoriales (idEditorial,nombre,idPais) VALUES ('{idEditorial}','{nombre}','{idPais}')"
        mi_cursor.execute(sql)
        mi_db.commit()

    def teardown_class(self):
        # Limpiar editoriales de prueba
        mi_cursor.execute("DELETE FROM editoriales WHERE idEditorial IN ('e01','e02')")
        mi_db.commit()

    def test_lista_editoriales(self):
        esperado = "editoriales"
        calculado = requests.get(self.url)
        assert calculado.status_code == 200
        assert calculado.json()["mensaje"] == esperado

    @pytest.mark.parametrize(
        ["nuevo_entrada","esperado_entrada"],
        [({"idEditorial":"e02","nombre":"Editorial Prueba","idPais":"MX"},"Editorial agregada con éxito"),  
         ({"idEditorial":"e01","nombre":"Editorial Norma","idPais":"PR"},"Id de editorial ya existe")]
    )
    def test_agregar(self, nuevo_entrada, esperado_entrada):
        calculado = requests.post(self.url, json=nuevo_entrada)
        assert calculado.status_code == 200
        assert esperado_entrada == calculado.json()["mensaje"]

    @pytest.mark.parametrize(
        ["id_entrada","esperado_entrada"], 
        [("e01","Editorial encontrado"),
         ("e09","Id no encontrado")]
    )
    def test_busqueda(self, id_entrada, esperado_entrada):
        idEditorial = id_entrada
        esperado = esperado_entrada
        calculado = requests.get(f"{self.url}/{idEditorial}")
        assert calculado.status_code == 200
        assert esperado == calculado.json()["mensaje"]
    
    def test_modifica1(self):
        idEditorial = "e02"
        nombre = "Editorial Norma Modificada"
        idPais = "PR"
        nuevo = {"idEditorial":idEditorial,"nombre":nombre,"idPais":idPais}
        esperado = "Editorial modificado con éxito"
        calculado = requests.put(f"{self.url}/{idEditorial}", json=nuevo)
        assert calculado.status_code == 200
        assert esperado == calculado.json()["mensaje"]

        sql = f"SELECT * FROM editoriales WHERE idEditorial='{idEditorial}'"
        mi_cursor.execute(sql)
        datos = mi_cursor.fetchall()[0]
        assert nombre == datos[1] and idPais == datos[2]

    def test_modifica2(self):
        idEditorial = "e09"
        nombre = "Editorial de Prueba Modificada"
        idPais = "PR"
        nuevo = {"idEditorial":idEditorial,"nombre":nombre,"idPais":idPais}
        esperado = "Editorial no existe"
        calculado = requests.put(f"{self.url}/{idEditorial}", json=nuevo)
        assert calculado.status_code == 200
        assert esperado == calculado.json()["mensaje"]
        
    @pytest.mark.parametrize(
        ["id_entrada","esperado_entrada"],
        [("e01","Editorial eliminada con éxito!"),
         ("e09","Editorial no existe")]
    )
    def test_elimina(self, id_entrada, esperado_entrada):
        idEditorial = id_entrada
        esperado = esperado_entrada
        calculado = requests.delete(f"{self.url}/{idEditorial}")
        assert calculado.status_code == 200
        assert esperado == calculado.json()["mensaje"]

        # Solo verificar en BD si esperábamos que existiera
        if esperado_entrada == "Editorial eliminada con éxito!":
            mi_db.commit()
            sql = f"SELECT * FROM editoriales WHERE idEditorial='{idEditorial}'"
            mi_cursor.execute(sql)
            datos = mi_cursor.fetchall()
            assert len(datos) == 0