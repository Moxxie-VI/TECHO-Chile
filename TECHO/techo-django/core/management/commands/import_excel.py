import pandas as pd
from django.core.management.base import BaseCommand
from core.models import Proyecto, Vivienda, Constructora, RegistroPostventa, FichaInmueble


class Command(BaseCommand):
    help = "Importa datos desde el Excel real de TECHO (ejemplo.xlsx) a las tablas Proyecto, Vivienda y RegistroPostventa."

    def add_arguments(self, parser):
        parser.add_argument("--file", required=True, help="Ruta del Excel")
        parser.add_argument("--sheet", default=0, help="Nombre o índice de hoja")

    def handle(self, *args, **opts):
        path = opts["file"]
        df = pd.read_excel(path, sheet_name=opts["sheet"])
        self.stdout.write(f"[OK] Archivo leido: {path} ({len(df)} filas)")

        # Mapea las columnas reales del Excel de TECHO
        required = ["PYTO_COD", "PYTO_NOMBRE", "CONSTRUCTORA", "COMUNA", "VDA_CODIGO", "VDA_TIPOLOGIA"]
        faltan = [c for c in required if c not in df.columns]
        if faltan:
            self.stderr.write(self.style.ERROR(f"[ERROR] Faltan columnas requeridas: {faltan}"))
            return

        count_p = 0
        count_c = 0
        count_v = 0
        count_r = 0

        for _, row in df.iterrows():
            cod_proy = str(row["PYTO_COD"]).strip()
            nom_proy = str(row["PYTO_NOMBRE"]).strip()
            nom_const = str(row["CONSTRUCTORA"]).strip()
            comuna = str(row["COMUNA"]).strip() if not pd.isna(row["COMUNA"]) else ""

            # --- Constructora ---
            cons, new_c = Constructora.objects.get_or_create(
                nombre=nom_const,
                defaults={"rut": "00000000-0"}
            )
            if new_c:
                count_c += 1

            # --- Proyecto ---
            proy, new_p = Proyecto.objects.get_or_create(
                codigo=cod_proy,
                defaults={
                    "nombre": nom_proy,
                    "ubicacion": comuna,
                    "constructora": cons
                }
            )
            if new_p:
                count_p += 1

            # --- Vivienda ---
            tipo = str(row["VDA_TIPOLOGIA"]).strip().upper()[:20] if not pd.isna(row["VDA_TIPOLOGIA"]) else "CASA"
            viv = Vivienda.objects.create(
                proyecto=proy,
                tipo=tipo,
                modelo=row.get("RECINTO_TIPOLOGIA", "S/I"),
                cant_cuartos=None,
                cant_banos=None,
                piso=""
            )
            count_v += 1

            # --- Ficha ---
            ficha = FichaInmueble.objects.create(
                proyecto=proy,
                vivienda=viv
            )

            # --- Registro de postventa ---
            if not pd.isna(row.get("PV_DESCRIPCION")):
                RegistroPostventa.objects.create(
    proyecto=proy,
    ficha=ficha,
    recinto=row.get("RECINTO_NOMBRE", "S/I"),   # ← campo correcto según tu modelo
    observacion=row["PV_DESCRIPCION"],
    urgencia="ALTA" if str(row.get("PV_ESURGENTE", "")).strip().upper() == "SI" else "MEDIA"
)
                count_r += 1

        # --- Resumen final ---
        self.stdout.write(self.style.SUCCESS(
            f"[OK] Importacion completa:\n"
            f"   Constructoras nuevas: {count_c}\n"
            f"   Proyectos nuevos: {count_p}\n"
            f"   Viviendas creadas: {count_v}\n"
            f"   Registros postventa: {count_r}"
        ))
