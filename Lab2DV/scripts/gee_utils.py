import ee

def autenticar_gee(proyecto_id):
    """Maneja la autenticación segura."""
    try:
        ee.Initialize(project=proyecto_id)
        print("Autenticación exitosa")
    except Exception as e:
        print(f"Error: {e}")
        ee.Authenticate()
        ee.Initialize(project=proyecto_id)

def mask_clouds(image):
    """Enmascara nubes usando QA60."""
    qa = image.select('QA60')
    cloud_bit_mask = 1 << 10
    cirrus_bit_mask = 1 << 11
    mask = qa.bitwiseAnd(cloud_bit_mask).eq(0).And(
           qa.bitwiseAnd(cirrus_bit_mask).eq(0))
    return image.updateMask(mask).divide(10000)
