#!/usr/bin/env python3
import argparse
import os
from io import BytesIO


def _positive_int(value: str) -> int:
    parsed = int(value)
    if parsed <= 0:
        raise argparse.ArgumentTypeError("La valeur doit être un entier positif")
    return parsed


def _aspect_ratio_from_size(width: int, height: int) -> str:
    ratio = width / height
    known_ratios = {
        "1:1": 1.0,
        "16:9": 16 / 9,
        "9:16": 9 / 16,
        "4:3": 4 / 3,
        "3:4": 3 / 4,
        "3:2": 3 / 2,
        "2:3": 2 / 3,
    }
    return min(known_ratios, key=lambda key: abs(known_ratios[key] - ratio))


class AssetGenerator:
    def __init__(self) -> None:
        try:
            from dotenv import load_dotenv

            load_dotenv()
        except ImportError:
            pass

        self.api_token = os.getenv("REPLICATE_API_TOKEN")
        if not self.api_token:
            raise ValueError(
                "REPLICATE_API_TOKEN manquant. Ajoutez-le dans un fichier .env à la racine."
            )
        try:
            import replicate
        except ImportError as exc:
            raise RuntimeError(
                "Dépendance manquante: installez les paquets avec `pip3 install -r requirements.txt`."
            ) from exc

        self.client = replicate.Client(api_token=self.api_token)

    def generate(
        self,
        prompt: str,
        engine: str = "fluxGen",
        negative: str = "",
        width: int = 1024,
        height: int = 1024,
        num: int = 1,
    ) -> list:
        try:
            import requests
            from PIL import Image
        except ImportError as exc:
            raise RuntimeError(
                "Dépendance manquante: installez les paquets avec `pip3 install -r requirements.txt`."
            ) from exc

        if engine == "fluxGen":
            output = self.client.run(
                "black-forest-labs/flux-schnell",
                input={
                    "prompt": prompt,
                    "num_outputs": num,
                    "aspect_ratio": _aspect_ratio_from_size(width, height),
                    "output_format": "png",
                    "output_quality": 100,
                },
            )
        else:
            output = self.client.run(
                "stability-ai/sdxl:39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b",
                input={
                    "prompt": prompt,
                    "negative_prompt": negative,
                    "width": width,
                    "height": height,
                    "num_outputs": num,
                    "scheduler": "DPMSolverMultistep",
                    "num_inference_steps": 25,
                    "guidance_scale": 7.5,
                },
            )

        images: list = []
        output_urls = output if isinstance(output, list) else [output]
        for image_url in output_urls:
            response = requests.get(image_url, timeout=60)
            response.raise_for_status()
            image = Image.open(BytesIO(response.content)).convert("RGBA")
            images.append(image)
        return images

    def resize_for_mobile(self, image, size: tuple[int, int] = (512, 512), keep_aspect: bool = True):
        from PIL import Image

        if keep_aspect:
            adapted = image.copy()
            adapted.thumbnail(size, Image.Resampling.LANCZOS)
            canvas = Image.new("RGBA", size, (0, 0, 0, 0))
            x_pos = (size[0] - adapted.width) // 2
            y_pos = (size[1] - adapted.height) // 2
            canvas.paste(adapted, (x_pos, y_pos), adapted)
            return canvas

        return image.resize(size, Image.Resampling.LANCZOS)

    def save(self, images: list, base_name: str, output_dir: str = "assets") -> list[str]:
        os.makedirs(output_dir, exist_ok=True)
        paths: list[str] = []
        for index, image in enumerate(images, start=1):
            path = os.path.join(output_dir, f"{base_name}_{index}.png")
            image.save(path)
            paths.append(path)
        return paths


def main() -> int:
    parser = argparse.ArgumentParser(description="Générateur d'assets premium pour jeux mobiles")
    parser.add_argument("--prompt", required=True, help="Description de l'asset souhaité")
    parser.add_argument(
        "--engine",
        choices=["fluxGen", "sdxl"],
        default="fluxGen",
        help="Moteur de génération (fluxGen recommandé)",
    )
    parser.add_argument(
        "--negative",
        default="low quality, blurry, ugly, deformed",
        help="Prompt négatif",
    )
    parser.add_argument("--width", type=_positive_int, default=1024, help="Largeur de génération")
    parser.add_argument("--height", type=_positive_int, default=1024, help="Hauteur de génération")
    parser.add_argument("--num", type=_positive_int, default=1, help="Nombre d'images à générer")
    parser.add_argument("--output", default="generated", help="Nom de base des fichiers")
    parser.add_argument(
        "--mobile",
        type=_positive_int,
        nargs=2,
        default=[512, 512],
        metavar=("W", "H"),
        help="Redimensionner pour mobile (ex: --mobile 512 512)",
    )
    parser.add_argument(
        "--no-resize",
        action="store_true",
        help="Ne pas redimensionner (garde la taille originale)",
    )
    parser.add_argument(
        "--output-dir",
        default="assets",
        help="Dossier de sortie pour les PNG générés",
    )
    args = parser.parse_args()

    generator = AssetGenerator()
    print(f"Génération de {args.num} image(s) avec le prompt : {args.prompt}")
    if args.engine == "fluxGen" and args.negative:
        print("Note: --negative est ignoré avec fluxGen.")
    images = generator.generate(
        prompt=args.prompt,
        engine=args.engine,
        negative=args.negative,
        width=args.width,
        height=args.height,
        num=args.num,
    )

    if not args.no_resize:
        target_size = tuple(args.mobile)
        images = [generator.resize_for_mobile(image, target_size) for image in images]
        print(f"Redimensionné pour mobile : {target_size[0]}x{target_size[1]}")

    paths = generator.save(images, args.output, args.output_dir)
    print("Assets sauvegardés :")
    for path in paths:
        print(f" - {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())