"""Author the assessed report from saved metrics and experiment figures."""
import json
from pathlib import Path
from docx import Document
from docx.shared import Inches,Pt,RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
ROOT=Path(__file__).resolve().parents[1];A=ROOT/'artifacts';OUT=ROOT/'report';OUT.mkdir(exist_ok=True)
r=json.loads((A/'results.json').read_text());env=json.loads((A/'environment.json').read_text());manifest=json.loads((A/'data_manifest.json').read_text());examples=json.loads((A/'selected_examples.json').read_text());training={v:json.loads((A/f'{v}_training.json').read_text()) for v in ['baseline','skip']}
delta=r['delta_miou']*100
outcome=f"Additive skip fusion {'improved' if delta>0 else 'reduced'} held-out mIoU by {abs(delta):.2f} percentage points under the fixed budget."
doc=Document();sec=doc.sections[0];sec.page_height=Inches(11.7);sec.page_width=Inches(8.3);sec.top_margin=Inches(.65);sec.bottom_margin=Inches(.65);sec.left_margin=Inches(.75);sec.right_margin=Inches(.75)
styles=doc.styles
for name in ['Normal','Body Text']:
    styles[name].font.name='Cambria';styles[name].font.size=Pt(11);styles[name].paragraph_format.space_after=Pt(7);styles[name].paragraph_format.line_spacing=1.08
for name,size in [('Title',29),('Subtitle',13),('Heading 1',18),('Heading 2',12),('Heading 3',11)]:
    styles[name].font.name='Calibri';styles[name].font.size=Pt(size);styles[name].font.color.rgb=RGBColor(0,0,0)
    styles[name].paragraph_format.space_before=Pt(10);styles[name].paragraph_format.space_after=Pt(7)
styles['Caption'].font.name='Calibri';styles['Caption'].font.size=Pt(9);styles['Caption'].font.color.rgb=RGBColor.from_string('444444')
footer=sec.footer.paragraphs[0];footer.alignment=WD_ALIGN_PARAGRAPH.RIGHT
run=footer.add_run('23115002  |  ');run.font.size=Pt(9)
fld=OxmlElement('w:fldSimple');fld.set(qn('w:instr'),'PAGE');footer._p.append(fld)
doc.core_properties.author='Abhay Kumar';doc.core_properties.title='Reproducible Pet Segmentation with Additive Skip Fusion';doc.core_properties.subject='Advanced Computer Vision assignment B'
def p(text,style=None):return doc.add_paragraph(text,style)
def h(text):doc.add_heading(text,1)
def sub(text):doc.add_heading(text,2)
def page(title):doc.add_page_break();h(title)
def table(headers,rows,widths=None):
    t=doc.add_table(rows=1,cols=len(headers));t.autofit=False
    if widths:
        for c,w in zip(t.columns,widths):c.width=Inches(w)
    for c,text in zip(t.rows[0].cells,headers):c.text=str(text)
    for row in rows:
        cells=t.add_row().cells
        for c,text in zip(cells,row):c.text=str(text)
    for ri,row in enumerate(t.rows):
        for ci,c in enumerate(row.cells):
            if widths: c.width=Inches(widths[ci])
            tcPr=c._tc.get_or_add_tcPr();borders=OxmlElement('w:tcBorders')
            for edge in ['top','left','bottom','right']:
                e=OxmlElement('w:'+edge);e.set(qn('w:val'),'single');e.set(qn('w:sz'),'4');e.set(qn('w:color'),'D9D9D9');borders.append(e)
            tcPr.append(borders);m=OxmlElement('w:tcMar')
            for edge in ['top','left','bottom','right']:
                e=OxmlElement('w:'+edge);e.set(qn('w:w'),'85');e.set(qn('w:type'),'dxa');m.append(e)
            tcPr.append(m)
            sh=OxmlElement('w:shd');sh.set(qn('w:fill'),'20394E' if ri==0 else ('F2F5F7' if ri%2==0 else 'FFFFFF'));tcPr.append(sh)
            for para in c.paragraphs:
                para.paragraph_format.space_after=Pt(2);para.paragraph_format.space_before=Pt(2);para.paragraph_format.line_spacing=1
                for run in para.runs:
                    run.font.name='Calibri';run.font.size=Pt(9.5);run.font.bold=ri==0
                    run.font.color.rgb=RGBColor.from_string('FFFFFF' if ri==0 else '000000')
            c.vertical_alignment=1
    repeat=OxmlElement('w:tblHeader');t.rows[0]._tr.get_or_add_trPr().append(repeat)
    doc.add_paragraph().paragraph_format.space_after=Pt(0)
    return t

def fig(file,caption,width=6.65):
    para=doc.add_paragraph();para.paragraph_format.space_after=Pt(3);para.alignment=WD_ALIGN_PARAGRAPH.CENTER
    para.add_run().add_picture(str(A/file),width=Inches(width))
    para.paragraph_format.keep_with_next=True
    cap=p(caption,'Caption');cap.paragraph_format.keep_with_next=False

def code(text):
    para=p(text);para.paragraph_format.line_spacing=1;para.paragraph_format.space_after=Pt(7)
    for run in para.runs:run.font.name='Courier New';run.font.size=Pt(9)

# Page 1
p('Reproducible Pet Segmentation\nwith Additive Skip Fusion','Title')
p('Advanced Computer Vision  |  Assignment B','Subtitle')
p('Abhay Kumar\nRoll number 23115002\nBatch 2027\n14 November 2026')
p('Submitted to Bunil Kumar Balabantaray\nAssistant Professor')
sub('Abstract')
p('This project evaluates one architectural mechanism in a controlled semantic segmentation experiment. A compact encoder–decoder and a parameter-matched variant with additive skip fusion are trained from scratch on a frozen, breed-balanced subset of the Oxford-IIIT Pet dataset. Human trimaps supply background and pet labels; uncertain boundary pixels are ignored. Both runs use the same seed, initialization, sample and augmentation schedule, optimizer, resolution and 20-epoch update budget.')
p(f"The baseline obtains {r['baseline']['miou']*100:.2f}% test mIoU and the skip variant obtains {r['skip']['miou']*100:.2f}%. {outcome} Each model has 24,674 parameters. Results are computed from a global valid-pixel confusion matrix over 740 held-out images. Latency is measured on an Apple M2 CPU under explicit conditions.")
p('The submission includes runnable code, pinned environment versions, split and hash manifests, selected checkpoints, raw training logs, the exact evaluation script, qualitative examples, failure cases and genuine browser screenshots of saved evidence. The experiment supports a comparison within this protocol; it does not establish statistical significance or full-dataset benchmark performance.')
sub('Project repository')
p('https://github.com/abhikhurannah/ACV')
sub('Research question')
p('Does adding two encoder-to-decoder feature additions improve segmentation overlap when the number of parameters and training updates are held constant?')

# Page 2
page('1 Introduction and background study')
p('Semantic segmentation assigns a class to every image pixel. Unlike image classification, it must recover object extent as well as recognize appearance. Downsampling in an encoder provides context at lower spatial resolution, while a decoder upsamples those features to a dense prediction. Fine structures can be difficult to reconstruct after repeated pooling.')
p('The practical task here is binary foreground segmentation of cats and dogs in varied photographic settings. Breed identity is used to balance sampling, while every breed shares the same pet output class. A modest model and small image size keep training feasible on a laptop and make the controlled comparison easy to inspect.')
sub('Background study')
p('The Oxford-IIIT Pet dataset provides pet photographs with breed metadata and pixel-level trimaps [1, 2]. Its human annotations make it suitable for evaluating predicted masks without using algorithm-generated pseudo-ground truth. This project uses a declared subset of the official pools and retains the original image IDs.')
p('U-Net combines a contracting path with an expanding path for localization [3]. The present network is inspired by that encoder–decoder structure, but is intentionally much smaller and uses additive fusion rather than U-Net concatenation. It is not an exact U-Net reproduction. Addition keeps decoder widths and parameter shapes identical, which makes the mechanism test especially direct.')
p('The hypothesis is that higher-resolution encoder features will help the decoder recover pet extent. The comparison tests this hypothesis empirically; it does not assume that adding a skip connection must improve the score. Optimization, low resolution, limited training and uncertain edges can affect the outcome.')
sub('Plan of action')
table(['Stage','Action and evidence'],[
('1 Data contract','Freeze source pools, target IDs, ignored labels, transforms and split manifests.'),
('2 Baseline','Train the small encoder–decoder from scratch with a fixed seed and update budget.'),
('3 Controlled change','Enable only two additive skip connections with unchanged parameter shapes.'),
('4 Evaluation','Select by validation mIoU, then evaluate the same held-out test subset once per selected checkpoint.'),
('5 Evidence','Save logs, per-class IoU, parameters, latency samples, source images, masks and failures.'),
('6 Reproduction','Verify metric edge cases, render the report, package artifacts and publish the code.')],[1.2,5.45])
p('The detailed executable plan is included in PLAN_OF_ACTION.md. Test measurements were produced after both training runs; no test-based hyperparameter tuning was performed.')

# Page 3
page('2 Data contract')
p('Dataset: Oxford-IIIT Pet [1, 2]. RGB images are read from the timm mirror pinned to revision 089695c834a7deb60505b7cc506672db1c31a6aa [4]. Trimaps and official split lists are downloaded from Oxford. Images and masks are joined by exact image ID. File and archive SHA256 values are retained.')
table(['Original trimap ID','Meaning','Training target','Loss and IoU'],[(1,'Pet foreground',1,'Included'),(2,'Background',0,'Included'),(3,'Uncertain boundary',255,'Ignored')],[1.35,2.1,1.25,1.95])
p('Breed IDs are 1 through 37 in the official lists. They are used only for stratified selection. The model predicts two segmentation classes: background 0 and pet 1. Boundary 255 is neither a third class nor background.')
table(['Partition','Official pool','Images per breed','Total'],[('Train','trainval.txt',40,'1,480'),('Validation','trainval.txt',10,370),('Test','test.txt',20,740)],[1.3,2.1,1.8,1.45])
p('A Python random.Random generator with seed 23115002 shuffles sorted IDs independently within each breed. For trainval, the first 40 IDs are training and the next 10 validation; the test selection takes the first 20 IDs per breed from its separate official pool. The remaining official images are unused. Splits are disjoint, and artifacts/splits.json records every chosen ID.')
p('Image transforms: decode and convert to RGB; resize directly to 96 × 96 using bilinear interpolation; convert to float32 and divide by 255. This square resize can distort aspect ratio. Masks use nearest-neighbour resizing before label remapping, preserving discrete IDs. Training alone uses a paired horizontal flip with probability 0.5. Validation and test have no augmentation.')
fig('figures/data_contract.png','Figure 1. A training image and its transformed human mask. Grey pixels are excluded from both optimization and scoring.',4.6)
p('After resizing, the test subset contains 3,897,740 valid background pixels, 2,069,115 valid pet pixels and 852,985 ignored pixels. This background imbalance motivates reporting both class IoUs and their unweighted mean.')

# Page 4
page('3 Methodology and proposed architecture')
p('The network accepts N × 3 × 96 × 96 tensors and emits N × 2 × 96 × 96 logits. Two max-pooling stages reduce spatial resolution to 24 × 24. Decoder stages use bilinear upsampling followed by channel projections and convolution blocks. The final prediction is the argmax of the two logits.')
fig('figures/architecture.png','Figure 2. Proposed architecture. Dashed paths are enabled only in the skip variant. The fusion coefficient g is a fixed switch and has no trainable parameters.')
table(['Block','Channels and output shape','Parameters'],[('Encoder E1','3→8→8; 8 × 96 × 96','808'),('Encoder E2','8→16→16; 16 × 48 × 48','3,488'),('Bottleneck','16→32→32; 32 × 24 × 24','13,888'),('Projection P2','1×1; 32→16; 16 × 48 × 48','528'),('Decoder D2','16→16→16; 16 × 48 × 48','4,640'),('Projection P1','1×1; 16→8; 8 × 96 × 96','136'),('Decoder D1','8→8→8; 8 × 96 × 96','1,168'),('Output head','1×1; 8→2; 2 × 96 × 96','18'),('Total','Same for both variants','24,674')],[1.35,4.05,1.25])
p('Each convolution block has two 3 × 3 convolutions, stride 1, padding 1, bias enabled, and ReLU after each. Max pools use 2 × 2 windows and stride 2. Bilinear interpolation uses align_corners=False. No pretrained weights, normalization layers, dropout, dilation, global pooling or boundary branch are used.')
p('For decoder level k, Dk = Block(Pk(Up(Dk+1)) + gEk). The baseline uses g = 0 and the variant uses g = 1. The Python implementation bypasses the additions when g = 0. Feature fusion is the only mechanism changed.')

# Page 5
page('4 Training and evaluation protocol')
table(['Setting','Value shared by both runs'],[('Seed and device','23115002; CPU; float32; four PyTorch threads'),('Initialization','Default PyTorch convolution initialization; identical seed and parameter shapes'),('Data and transforms','1,480 train / 370 validation; 96 × 96; paired horizontal flip p=0.5'),('Optimizer','Adam; learning rate 0.001; betas (0.9, 0.999); epsilon 1e-8; weight decay 0'),('Batch and update budget','16 images; 93 batches per epoch; last batch 8; 20 epochs; 1,860 updates per model'),('Loss','Cross entropy on valid pixels; ignore_index=255; no class weights'),('Stopping and selection','Stop after epoch 20; retain highest validation global mIoU; earliest epoch on a tie'),('Other controls','No scheduler, mixed precision, gradient clipping or hyperparameter search')],[1.5,5.15])
p('A separate seeded torch.Generator controls shuffled image order and flip decisions. Resetting it before each run gives both models the same training schedule. Deterministic PyTorch algorithms are enabled. Reproducibility is scoped to the recorded software and CPU environment; cross-platform bitwise equality is not guaranteed [5].')
sub('Accuracy measurement')
p('Evaluation uses model.eval() and torch.inference_mode(). For every valid pixel, the predicted argmax class contributes to a 2 × 2 confusion matrix C. Rows denote ground truth and columns prediction, in the order background, pet. The matrix is accumulated over the full test subset before computing ratios.')
code('IoU(c) = C[c,c] / (sum(C[c,:]) + sum(C[:,c]) - C[c,c])\nmIoU = (IoU(background) + IoU(pet)) / 2')
p('Ignored pixels are removed before the confusion matrix is updated. Reported mIoU is the mean of two global class IoUs, not the mean of per-image mIoU. Per-image values are saved only to select and diagnose qualitative examples. All test labels are human trimaps.')
sub('Latency conditions')
p('Hardware: Apple M2, 8 logical CPU cores, 8 GiB RAM; macOS 27.0.1 arm64. Software: Python 3.10.16, PyTorch 2.14.1 and NumPy 2.2.6. Timing uses four CPU threads, inference mode, float32, batch 1 and an already resident 1 × 3 × 96 × 96 tensor. Each model receives 30 warmups and 200 individually timed forward calls measured with time.perf_counter_ns().')
p('The latency measurement excludes image decoding, resizing, device or memory transfers, argmax and metric calculation. Median, mean, p95 and all raw timing samples are retained. Thermal state and background processes were not controlled; these timings describe this machine and session, not an end-to-end application guarantee.')

# Page 6
page('5 Results and interpretation')
table(['Measure','Baseline','Additive skip'],[
('Background IoU',f"{r['baseline']['background_iou']*100:.2f}%",f"{r['skip']['background_iou']*100:.2f}%"),
('Pet IoU',f"{r['baseline']['pet_iou']*100:.2f}%",f"{r['skip']['pet_iou']*100:.2f}%"),
('Mean IoU',f"{r['baseline']['miou']*100:.2f}%",f"{r['skip']['miou']*100:.2f}%"),
('Selected epoch',r['baseline']['best_epoch'],r['skip']['best_epoch']),
('Parameters','24,674','24,674'),
('Training time',f"{training['baseline']['seconds']:.1f} s",f"{training['skip']['seconds']:.1f} s"),
('CPU median latency',f"{r['baseline']['latency_ms']['median']:.3f} ms",f"{r['skip']['latency_ms']['median']:.3f} ms"),
('CPU p95 latency',f"{r['baseline']['latency_ms']['p95']:.3f} ms",f"{r['skip']['latency_ms']['p95']:.3f} ms")],[2.65,2,2])
p(outcome+' False pet predictions on background decrease from 484,703 to 352,442 pixels, while missed pet pixels increase from 464,153 to 531,816. This indicates more conservative foreground prediction; both class IoUs still improve. The comparison is parameter-matched and update-matched. Skip addition still introduces activation additions and can change memory access, so equal parameter count does not imply identical computation or training time. A single-seed difference is descriptive evidence, not a statistical significance claim.')
fig('figures/learning_curves.png','Figure 3. Measured training losses and validation global mIoU. Dots mark the selected validation checkpoints. All 20 epochs are retained in the raw logs.',6.65)

# Page 7
page('6 Qualitative results')
p('Examples are selected automatically at the 25th, 50th and 75th percentiles of the skip model’s per-image mIoU ranking. This fixed selection rule shows variation in performance instead of presenting only the strongest predictions. It is applied after evaluation and does not affect model selection.')
fig('figures/representative.png','Figure 4. Source RGB, transformed human mask and both predictions. Scores under prediction panels are individual-image mIoUs; they are not the aggregate test score.',6.65)
p('All four columns use the same resized 96 × 96 grid. Grey marks the uncertain region of the human annotation. Predictions assign a class everywhere, but predictions inside those grey ground-truth regions do not contribute to IoU. Source IDs allow every panel to be traced to the frozen manifest.')
p('Comparing the two prediction columns reveals whether feature fusion changes object extent on the same input. Overlap metrics summarize region agreement, while these panels expose local shape differences that one global number cannot explain. Fine fur and narrow limbs remain limited by the small working resolution.')

# Page 8
page('7 Failure cases and practical limits')
p('The following are the three lowest per-image mIoU examples for the skip model across the complete test subset. Ranking uses valid pixels and averages defined class IoUs; a class with zero union is omitted only from that image score. These cases document remaining weaknesses even if the aggregate comparison favours the modified model.')
fig('figures/failures.png','Figure 5. The three worst skip-model test cases, selected by measured score. Input IDs and both model scores are retained for independent inspection.',6.65)
p('In pomeranian_89, the annotated pet occupies almost the whole image, but both models predict a smaller central region. In Persian_97, most of the cat is missed; skip fusion leaves only a small foreground patch. In keeshond_7, both models identify part of the visible animal, but the official mask is entirely background, so those predictions are counted as false positives. This last case demonstrates why a low score can reflect an annotation limitation as well as model error. The images do not establish a causal explanation for the model failures.')
p('Two test trimaps, keeshond_7 and Persian_259, and two training trimaps, Egyptian_Mau_165 and miniature_pinscher_14, contain only background at their original resolution. They remain in the frozen evaluation; they limit the interpretation of image-level failures and aggregate scores. The annotation audit is included in artifacts/annotation_audit.json. A useful next experiment would retain this exact split and vary only resolution, followed separately by a multi-seed repeat of the skip comparison. Boundary-sensitive evaluation would require an explicitly defined protocol because uncertain boundary pixels are ignored here. Those extensions have not been run and are not presented as results.')

# Page 9
page('8 Screenshots of execution evidence')
p('These are genuine browser screenshots of local evidence pages built directly from saved training logs, checks and results. They are evidence dashboard views, not terminal captures. The underlying JSON, log files, HTML and capture script are included so that the figures can be checked against their sources.')
fig('screenshots/execution.png','Screenshot 1. Completed fixed-budget training excerpts, data and metric checks, and frozen execution settings.',6.65)
fig('screenshots/metrics.png','Screenshot 2. Held-out metrics, confusion matrices and measured latency conditions for both selected checkpoints.',6.65)

# Page 10
page('9 Reproduction and conclusion')
sub('Exact execution sequence')
code('python3.10 -m venv .venv\nsource .venv/bin/activate\npip install -r requirements-lock.txt\npython src/download.py\npython src/prepare.py\npython src/check_contract.py\npython -u src/train.py --variant baseline > artifacts/baseline_train.log 2>&1\npython -u src/train.py --variant skip > artifacts/skip_train.log 2>&1\npython src/evaluate.py\npython src/figures.py\npython src/build_evidence.py')
p('Download hashes are checked against artifacts/archive_hashes.json. The split manifest is frozen in artifacts/splits.json; data_manifest.json records the source hashes and counts. The exact evaluator is src/evaluate.py. Selected weights are provided in the submission archive as artifacts/baseline.pt and artifacts/skip.pt. Run evaluation directly after preparing the data to check those saved weights without retraining.')
sub('Verification')
p('Automated checks confirm split sizes and disjointness, legal mask IDs, input dimensions, identical model parameter shapes and a hand-calculated IoU example. A perfect prediction returns IoU 1, and changing a prediction at an ignored pixel leaves the score unchanged. Checkpoint re-evaluation reproduces the saved accuracy values. Report pages are rendered and visually inspected.')
sub('What the experiment does not establish')
p('This experiment uses one seed, a selected subset of one dataset, 96 × 96 square-resized inputs and a short fixed budget. It does not establish statistical significance, full-dataset performance, robustness to domain shift, optimal hyperparameters, full-resolution boundary quality or superiority over modern segmentation models. It does not test concatenative fusion, dilation, global pooling or a boundary branch.')
p('Ignoring uncertain boundary pixels reduces sensitivity to edge errors. Breed-balanced sampling does not remove background or photographic biases. Matching updates and parameters controls two major budget factors but does not equalize exact FLOPs or memory traffic. CPU forward timings cannot be transferred directly to another device or to a full application pipeline.')
sub('Conclusion')
p(outcome+f" The measured test mIoU changes from {r['baseline']['miou']*100:.2f}% to {r['skip']['miou']*100:.2f}% with the same 24,674 parameters and 1,860 updates per run. The submission demonstrates a reproducible way to isolate skip fusion while retaining exact data, training and evaluation evidence. Repeating the protocol across multiple seeds is the next step before making a stronger general claim.")

# Page 11
page('10 References and submission contents')
refs=[
'[1] O. M. Parkhi, A. Vedaldi, A. Zisserman and C. V. Jawahar. Cats and Dogs. IEEE Conference on Computer Vision and Pattern Recognition, 2012. Dataset and human trimaps: https://www.robots.ox.ac.uk/~vgg/data/pets/',
'[2] Torchvision maintainers. Oxford-IIIT Pet dataset implementation and trimap convention. https://github.com/pytorch/vision/blob/main/torchvision/datasets/oxford_iiit_pet.py ; boundary convention discussed at https://github.com/pytorch/vision/issues/8364',
'[3] O. Ronneberger, P. Fischer and T. Brox. U-Net Convolutional Networks for Biomedical Image Segmentation. MICCAI, 2015. https://arxiv.org/abs/1505.04597',
'[4] timm dataset mirror. Oxford-IIIT Pet. Revision 089695c834a7deb60505b7cc506672db1c31a6aa. https://huggingface.co/datasets/timm/oxford-iiit-pet/tree/089695c834a7deb60505b7cc506672db1c31a6aa',
'[5] PyTorch contributors. Reproducibility documentation. https://docs.pytorch.org/docs/2.14/notes/randomness.html',
'[6] Creative Commons. Attribution ShareAlike 4.0 International. https://creativecommons.org/licenses/by-sa/4.0/']
for ref in refs:p(ref)
p('Online sources consulted on 14 November 2026. Dataset photographs remain copyrighted by their original owners. The official dataset page lists CC BY-SA 4.0. Included source images are resized and masks recoloured; attribution and derivative-image terms are recorded in DATA_ATTRIBUTION.md.')
sub('Submission contents')
table(['Location','Contents'],[('report/23115002.docx and PDF','Assessed report, figures and screenshots'),('src/','Download, preparation, model, training, exact evaluation and evidence code'),('artifacts/','Split and hash manifests, raw histories, logs, measurements and selected weights'),('artifacts/figures and screenshots','Architecture, measured plots, test examples and genuine evidence captures'),('requirements-lock.txt','Exact installed Python package versions'),('PLAN_OF_ACTION.md and README.md','Execution plan, reproduction commands and methodological limits')],[2.5,4.15])
p('Repository: https://github.com/abhikhurannah/ACV\nThe GitHub project excludes downloaded data and the virtual environment. Selected model checkpoints are included in the repository and submission archive. The report is named after roll number 23115002.')
# Strip inherited title and paragraph rules from the default Word template.
for root in [doc.styles.element, doc.element]:
    for border in list(root.xpath('.//w:pBdr')):
        border.getparent().remove(border)
doc.save(OUT/'23115002.docx')
print(OUT/'23115002.docx')
