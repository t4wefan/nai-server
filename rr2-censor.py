import uvicorn
import base64
from pydantic import BaseModel, Field
from fastapi import FastAPI
import io
from typing import List
import torch
import torch.nn as nn
from transformers import (
    CLIPConfig,
    CLIPVisionModel,
    PreTrainedModel,
    AutoFeatureExtractor,
)
from PIL import Image

# device = torch.device('cuda', 0)
if False:
    print("using GPU")
    device = torch.device("cuda")
    torch.backends.cudnn.enabled = True
    torch.backends.cudnn.allow_tf32 = True
    torch.backends.cuda.matmul.allow_tf32 = True
else:
    print("using CPU")
    device = torch.device("cpu")

@torch.compile
def cosine_distance(image_embeds, text_embeds):
    normalized_image_embeds = nn.functional.normalize(image_embeds.to(device))
    normalized_text_embeds = nn.functional.normalize(text_embeds)
    return torch.mm(normalized_image_embeds, normalized_text_embeds.t())


class StableDiffusionSafetyChecker(PreTrainedModel):
    config_class = CLIPConfig

    def __init__(self, config: CLIPConfig):
        super().__init__(config)
        self.vision_model = CLIPVisionModel(config.vision_config).to(device)
        self.visual_projection = nn.Linear(
            config.vision_config.hidden_size, config.projection_dim, bias=False
        ).to(device)
        self.concept_embeds = nn.Parameter(
            torch.ones(17, config.projection_dim).to(device), requires_grad=False
        ).to(device)
        self.register_buffer("concept_embeds_weights", torch.ones(17).to(device))

    @torch.inference_mode()
    @torch.compile
    def forward(self, clip_input):
        pooled_output = self.vision_model(clip_input.to(device))[1]  # pooled_output
        image_embeds = self.visual_projection(pooled_output)
        cos_dist = cosine_distance(image_embeds, self.concept_embeds).to(device)
        concept_scores = cos_dist - self.concept_embeds_weights
        return concept_scores


app = FastAPI()
safety_model_id = "CompVis/stable-diffusion-safety-checker"
safety_feature_extractor = AutoFeatureExtractor.from_pretrained(safety_model_id)
safety_checker = StableDiffusionSafetyChecker.from_pretrained(safety_model_id)


class NsfwCheck(BaseModel):
    image: str = Field(
        description="The base64 encoded image data.",
        default="base64://",
        required=True,
    )


class ReviewResult(BaseModel):
    concept_scores: List[float] = Field(
        description="A list of 17 floats representing the scores of various concepts in the image, "
        + "where a higher score indicates a higher likelihood of the concept being present in the image.",
        default=[0.0 for _ in range(17)],
    )


@app.post("/check_safety")
def check_safety(data: NsfwCheck):
    """
    Check the safety of an image.
    """
    print("Got")

    image = Image.open(io.BytesIO(base64.b64decode(data.image))).convert("RGB")
    safety_checker_input = safety_feature_extractor(image, return_tensors="pt")
    concept_scores = safety_checker(clip_input=safety_checker_input.pixel_values)
    # if concept_scores:
    #     image.save("img/" + str(uuid.uuid4()) + ".jpg")
    # else:
    #     image.save("img2/" + str(uuid.uuid4()) + ".jpg")
    print(concept_scores)
    concept_scores = concept_scores.cpu().numpy()[0].tolist()
    print(concept_scores)
    return ReviewResult(concept_scores=concept_scores)


if __name__ == "__main__":
    uvicorn.run(app=app, host="0.0.0.0", port=16001)