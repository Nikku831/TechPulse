import subprocess

def generate_plantuml_image(uml_file_path, output_image_path):

    plantuml_jar_path = "plantuml-1.2024.7.jar"  
    subprocess.run(["java", "-jar", plantuml_jar_path, uml_file_path])
    
    generated_image_path = uml_file_path.replace(".puml", ".png")
    subprocess.run(["mv", generated_image_path, output_image_path])
