import datetime
import uuid
from loguru import logger
from typing import List, Optional
from swarms import Agent, InteractiveGroupChat, count_tokens
from swarms.prompts.ag_prompt import aggregator_system_prompt_main
from mri_swarm.prompts import GROUPCHAT_INITIATE_PROMPT

# Anatomical Structure Analysis Agent
anatomical_agent = Agent(
    agent_name="MRI-Anatomical-Analysis-Agent",
    agent_description="Specialized in anatomical structure analysis from MRI scans",
    system_prompt="""You are an expert MRI anatomical analysis agent specialized in:
    - Detailed anatomical structure identification
    - Brain region mapping and segmentation
    - Tissue type classification
    - Structural abnormality detection
    - Volumetric analysis of brain regions
    - Anatomical landmark identification
    - Cross-sectional anatomy interpretation
    
    Your core responsibilities include:
    1. Identifying and mapping brain structures
    2. Analyzing structural relationships
    3. Detecting anatomical variations
    4. Assessing tissue integrity
    5. Evaluating brain region volumes
    
    You maintain strict adherence to:
    - Anatomical terminology accuracy
    - Structural relationship understanding
    - 3D spatial orientation
    - Anatomical variation awareness
    - Standard anatomical nomenclature""",
    max_loops=1,
    model_name="claude-3-sonnet-20240229",
    dynamic_temperature_enabled=True,
    streaming_on=True,
)

# Pathology Detection Agent
pathology_agent = Agent(
    agent_name="MRI-Pathology-Detection-Agent",
    agent_description="Specialized in identifying pathological conditions in MRI scans",
    system_prompt="""You are an expert MRI pathology detection agent specialized in:
    - Tumor detection and classification
    - Lesion identification and characterization
    - Inflammatory condition assessment
    - Neurodegenerative disease markers
    - Vascular abnormality detection
    - White matter disease evaluation
    - Structural pathology identification
    
    Your core responsibilities include:
    1. Detecting pathological conditions
    2. Characterizing abnormal findings
    3. Assessing disease progression
    4. Identifying critical markers
    5. Evaluating treatment responses
    
    You maintain strict adherence to:
    - Diagnostic accuracy
    - Pathological classification systems
    - Disease pattern recognition
    - Clinical correlation
    - Evidence-based interpretation""",
    max_loops=1,
    model_name="claude-3-sonnet-20240229",
    dynamic_temperature_enabled=True,
    streaming_on=True,
)

# Sequence Analysis Agent
sequence_agent = Agent(
    agent_name="MRI-Sequence-Analysis-Agent",
    agent_description="Specialized in analyzing different MRI sequences and their implications",
    system_prompt="""You are an expert MRI sequence analysis agent specialized in:
    - T1/T2 weighted image interpretation
    - FLAIR sequence analysis
    - Diffusion-weighted imaging
    - Contrast enhancement patterns
    - Advanced sequence protocols
    - Artifact identification
    - Sequence optimization
    
    Your core responsibilities include:
    1. Analyzing multiple MRI sequences
    2. Interpreting signal characteristics
    3. Identifying sequence-specific findings
    4. Evaluating contrast patterns
    5. Detecting imaging artifacts
    
    You maintain strict adherence to:
    - Sequence-specific interpretation
    - Signal intensity analysis
    - Protocol optimization
    - Artifact recognition
    - Technical parameter understanding""",
    max_loops=1,
    model_name="claude-3-sonnet-20240229",
    dynamic_temperature_enabled=True,
    streaming_on=True,
)

# Quantitative Analysis Agent
quantitative_agent = Agent(
    agent_name="MRI-Quantitative-Analysis-Agent",
    agent_description="Specialized in quantitative measurements and analysis of MRI data",
    system_prompt="""You are an expert MRI quantitative analysis agent specialized in:
    - Volumetric measurements
    - Signal intensity quantification
    - Texture analysis
    - Statistical analysis of imaging data
    - Quantitative biomarker assessment
    - ROI analysis
    - Longitudinal change measurement
    
    Your core responsibilities include:
    1. Performing quantitative measurements
    2. Analyzing imaging biomarkers
    3. Conducting statistical analyses
    4. Tracking longitudinal changes
    5. Generating quantitative reports
    
    You maintain strict adherence to:
    - Measurement accuracy
    - Statistical rigor
    - Standardized methodologies
    - Quality control
    - Data validation""",
    max_loops=1,
    model_name="claude-3-sonnet-20240229",
    dynamic_temperature_enabled=True,
    streaming_on=True,
)

# Clinical Correlation Agent
clinical_agent = Agent(
    agent_name="MRI-Clinical-Correlation-Agent",
    agent_description="Specialized in correlating MRI findings with clinical presentation",
    system_prompt="""You are an expert MRI clinical correlation agent specialized in:
    - Clinical symptom correlation
    - Diagnostic criteria application
    - Treatment response assessment
    - Clinical outcome prediction
    - Medical history integration
    - Differential diagnosis development
    - Clinical recommendation formulation
    
    Your core responsibilities include:
    1. Correlating imaging with symptoms
    2. Applying diagnostic criteria
    3. Assessing treatment effects
    4. Developing clinical recommendations
    5. Integrating patient history
    
    You maintain strict adherence to:
    - Clinical guidelines
    - Evidence-based practice
    - Patient-specific context
    - Diagnostic accuracy
    - Clinical relevance""",
    max_loops=1,
    model_name="claude-3-sonnet-20240229",
    dynamic_temperature_enabled=True,
    streaming_on=True,
)

# Quality Control Agent
quality_agent = Agent(
    agent_name="MRI-Quality-Control-Agent",
    agent_description="Specialized in assessing and ensuring MRI image quality",
    system_prompt="""You are an expert MRI quality control agent specialized in:
    - Image quality assessment
    - Artifact detection and classification
    - Protocol compliance verification
    - Motion correction evaluation
    - Signal-to-noise ratio analysis
    - Image registration assessment
    - Quality assurance protocols
    
    Your core responsibilities include:
    1. Evaluating image quality
    2. Detecting technical issues
    3. Assessing protocol adherence
    4. Identifying artifacts
    5. Recommending quality improvements
    
    You maintain strict adherence to:
    - Quality standards
    - Technical specifications
    - Protocol guidelines
    - Artifact recognition
    - Quality metrics""",
    max_loops=1,
    model_name="claude-3-sonnet-20240229",
    dynamic_temperature_enabled=True,
    streaming_on=True,
)

summary_agent = Agent(
    agent_name="MRI-Summary-Agent",
    agent_description="Specialized in summarizing the analysis of MRI scans",
    system_prompt=aggregator_system_prompt_main,
    max_loops=1,
    model_name="claude-3-sonnet-20240229",
    dynamic_temperature_enabled=True,
    streaming_on=True,
    output_type="str-all-except-first",
)

# List of all agents for easy access
mri_agents = [
    anatomical_agent,
    sequence_agent,
    quantitative_agent,
    clinical_agent,
    quality_agent,
]


def groupchat_mri_analysis(task: str, img: str = None, imgs: List[str] = None):
    """
    Run MRI analysis using the interactive group chat of specialized MRI agents.

    This function orchestrates a collaborative analysis session where multiple
    specialized MRI agents (anatomical, pathology, sequence, quantitative,
    clinical, and quality agents) work together to analyze MRI scans.

    Args:
        task (str): The analysis task or question to be addressed by the MRI agents.
                   This could be a specific clinical question, quality assessment,
                   or general analysis request.
        img (str, optional): Path or identifier for a single MRI image to analyze.
                           Defaults to None.
        imgs (List[str], optional): List of paths or identifiers for multiple
                                  MRI images to analyze. Defaults to None.

    Returns:
        str: The collaborative analysis output from all MRI agents working together.
             This includes insights from anatomical, pathology, sequence,
             quantitative, clinical, and quality perspectives.

    Example:
        >>> result = groupchat_mri_analysis(
        ...     task="Analyze this brain MRI for any abnormalities",
        ...     img="path/to/brain_mri.jpg"
        ... )
        >>> print(result)
    """
    swarm = InteractiveGroupChat(
        name="MRI-Swarm",
        agents=mri_agents,
        description="You are a group of MRI agents that are working together to analyze MRI scans. You are all specialized in different aspects of MRI analysis and you are working together to provide a comprehensive analysis of the MRI scan.",
        # speaker_function="random-speaker",
        max_loops=1,
        output_type="all",
    )
    return swarm.run(task=task, img=img, imgs=imgs)


def mri_swarm(
    task: str,
    additional_patient_info: Optional[str] = None,
    img: str = None,
    imgs: List[str] = None,
    return_log: bool = False,
):
    """
    Perform comprehensive MRI analysis with collaborative agent discussion and summary.

    This function provides a two-stage MRI analysis:
    1. First, it runs a collaborative analysis using multiple specialized MRI agents
       that discuss and analyze the scans together
    2. Then, it generates a concise summary of the collaborative findings

    The function leverages the expertise of specialized agents including:
    - Anatomical analysis agent
    - Pathology detection agent
    - Sequence optimization agent
    - Quantitative measurement agent
    - Clinical correlation agent
    - Quality assessment agent

    Args:
        task (str): The analysis task or clinical question to be addressed.
                   Examples: "Detect brain lesions", "Assess image quality",
                   "Measure ventricular volume", "Identify artifacts"
        img (str, optional): Path or identifier for a single MRI image.
                           Can be a file path, URL, or image identifier.
                           Defaults to None.
        imgs (List[str], optional): List of paths or identifiers for multiple
                                  MRI images. Useful for comparing multiple scans
                                  or analyzing a series. Defaults to None.

    Returns:
        str: A comprehensive summary of the collaborative MRI analysis,
             distilling insights from all specialized agents into a coherent
             clinical report.

    Raises:
        AgentNotFoundError: If any of the required MRI agents are not available
        InvalidTaskFormatError: If the task format is invalid or unclear
        NoMentionedAgentsError: If no agents are mentioned in the task

    Example:
        >>> summary = mri_swarm(
        ...     task="Analyze this brain MRI for signs of multiple sclerosis",
        ...     img="patient_001_brain_mri.jpg"
        ... )
        >>> print(summary)
        # Output: Comprehensive analysis summary with findings from all agents

    Note:
        The function uses a random speaker function for agent interaction,
        ensuring diverse perspectives are captured in the analysis.
    """
    logger.info(f"Running MRI-Swarm analysis with task: {task}")

    groupchat_analysis = groupchat_mri_analysis(
        task=f"{GROUPCHAT_INITIATE_PROMPT}\n\nMain task: {task}\n\nPatient info: {additional_patient_info}",
        img=img,
        imgs=imgs,
    )

    logger.info("Main diaganosis analysis is complete, now generating summary")

    summary = summary_agent.run(
        f"Summarize the following MRI analysis: {groupchat_analysis} by your team of agents and provide a concise and detailed report of the findings, along with an array of potential diagnoses including the likelihood of each diagnosis and the rationale with supporting evidence for each diagnosis."
    )

    if return_log:
        return {
            "id": str(uuid.uuid4()),
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "task": task,
            "number_of_agents": len(mri_agents) + 1,
            "groupchat_analysis": groupchat_analysis,
            "summary": summary,
            "tokens_used": count_tokens(groupchat_analysis) + count_tokens(summary),
        }
    else:
        return summary


def batched_mri_swarm(
    tasks: List[str],
    patient_infos: List[str],
    imgs: List[str],
    return_log: bool = True,
):
    """
    Perform batch MRI analysis with collaborative agent discussion and summary.

    This function processes multiple MRI analysis tasks in sequence, applying the same
    collaborative swarm intelligence approach used in the single analysis function.
    Each task is processed independently with its corresponding patient information
    and image, allowing for efficient batch processing of multiple cases.

    Args:
        tasks (List[str]): List of analysis tasks or clinical questions for each case.
                          Each task should be a clear, specific instruction for MRI analysis.
        patient_infos (List[str]): List of patient information strings corresponding to each task.
                                  Can include age, medical history, symptoms, or other relevant details.
        imgs (List[str]): List of image file paths or URLs corresponding to each task.
                         Each image should be a valid MRI scan in supported format.
        return_log (bool, optional): If True, returns detailed analysis logs including
                                   agent interactions, token usage, and timestamps.
                                   If False, returns only the final summary for each case.
                                   Defaults to False.

    Returns:
        List[Union[str, Dict]]: List of analysis results, where each result corresponds
                               to one task. If return_log is True, each result is a dictionary
                               containing detailed analysis information. If return_log is False,
                               each result is a string containing the analysis summary.

    Raises:
        ValueError: If the lengths of tasks, patient_infos, and imgs lists are not equal
        AgentNotFoundError: If any of the required MRI agents are not available
        InvalidTaskFormatError: If any task format is invalid or unclear
        NoMentionedAgentsError: If no agents are mentioned in any task

    Example:
        >>> tasks = [
        ...     "Analyze this brain MRI for signs of multiple sclerosis",
        ...     "Evaluate this spine MRI for disc herniation"
        ... ]
        >>> patient_infos = [
        ...     "Patient age: 35, symptoms: vision problems, fatigue",
        ...     "Patient age: 45, symptoms: lower back pain, radiating to leg"
        ... ]
        >>> imgs = ["patient_001_brain.jpg", "patient_002_spine.jpg"]
        >>> results = batched_mri_swarm(tasks, patient_infos, imgs)
        >>> for i, result in enumerate(results):
        ...     print(f"Case {i+1}: {result}")
        # Output: List of analysis summaries for each case

    Note:
        - All input lists must have the same length
        - Each case is processed sequentially, not in parallel
        - The function maintains the same quality and depth of analysis as single cases
        - Processing time scales linearly with the number of cases
    """
    # Validate input list lengths
    if not (len(tasks) == len(patient_infos) == len(imgs)):
        raise ValueError(
            "All input lists (tasks, patient_infos, imgs) must have the same length"
        )

    results = []
    for task, patient_info, img in zip(tasks, patient_infos, imgs):
        results.append(
            mri_swarm(
                task=task,
                additional_patient_info=patient_info,
                img=img,
                return_log=return_log,
            )
        )

    return results
