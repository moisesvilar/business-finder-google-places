from openai_client import OpenAIClient

def main():
    texto = """
    Docuten es una plataforma de facturación electrónica que permite a las empresas gestionar sus facturas de forma digital. 
    Ofrece soluciones para la emisión, recepción y almacenamiento de facturas electrónicas, cumpliendo con la normativa vigente. 
    La plataforma está diseñada para ser intuitiva y fácil de usar, permitiendo a los usuarios gestionar sus documentos fiscales de manera eficiente.
    """
    client = OpenAIClient()
    resumen = client.resumir_texto(texto)
    if resumen:
        print("Resumen generado:")
        print(resumen)
    else:
        print("Error al generar el resumen.")

if __name__ == "__main__":
    main() 