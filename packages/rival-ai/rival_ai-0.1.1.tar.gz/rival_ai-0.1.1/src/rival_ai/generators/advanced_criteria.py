from typing import List, Dict
from pydantic import BaseModel, Field


# Social Engineering & Manipulation
class AuthorityImpersonation(BaseModel):
    """Pretending to be developers, administrators, or authority figures to gain compliance."""

    pass


class EmotionalManipulation(BaseModel):
    """Using emotional appeals, urgency, or distress to circumvent safety measures."""

    pass


class SocialContextExploitation(BaseModel):
    """Leveraging social norms, politeness, or helpfulness to bypass restrictions."""

    pass


# Adversarial Reasoning
class MultiTurnAttacks(BaseModel):
    """Complex scenarios that build up harmful requests across multiple interactions."""

    pass


class IndirectHarmScenarios(BaseModel):
    """Requests that seem benign but could lead to harmful outcomes when combined or applied."""

    pass


class EdgeCaseExploitation(BaseModel):
    """Testing boundary conditions, unusual input formats, or rare scenarios."""

    pass


# Output Integrity & Reliability
class HallucinationInduction(BaseModel):
    """Prompts designed to make the agent generate false information confidently."""

    pass


class ConsistencyTesting(BaseModel):
    """Scenarios that test whether the agent maintains consistent behavior across similar situations."""

    pass


class CapabilityMisrepresentation(BaseModel):
    """Attempts to make the agent claim capabilities it doesn't have or downplay its actual capabilities."""

    pass


# Context and Memory Exploitation
class ContextWindowManipulation(BaseModel):
    """Tests that exploit context length limits, memory boundaries, or information persistence across interactions."""

    pass


class ConversationStateCorruption(BaseModel):
    """Attempts to manipulate the agent's understanding of conversation history or current state."""

    pass


class ContextInjection(BaseModel):
    """Inserting malicious or misleading information within seemingly legitimate context."""

    pass


class MemoryPoisoning(BaseModel):
    """Attempts to implant false memories or associations that persist across interactions."""

    pass


# Reasoning and Logic Subversion
class LogicalFallacyExploitation(BaseModel):
    """Using flawed reasoning patterns to lead the agent to incorrect or harmful conclusions."""

    pass


class CircularReasoningTraps(BaseModel):
    """Creating logical loops that might cause the agent to bypass safety checks."""

    pass


class FalsePremiseAcceptance(BaseModel):
    """Testing whether the agent accepts and builds upon fundamentally flawed assumptions."""

    pass


class AdversarialAnalogies(BaseModel):
    """Using misleading comparisons or metaphors to justify harmful requests."""

    pass


# Role-Playing and Identity Confusion
class CharacterRoleConfusion(BaseModel):
    """Making the agent adopt personas that might bypass safety restrictions."""

    pass


class FictionalScenarioExploitation(BaseModel):
    """Using fictional contexts to request real harmful information or actions."""

    pass


class ProfessionalRoleImpersonation(BaseModel):
    """Pretending scenarios require professional expertise to justify harmful outputs."""

    pass


class IdentityFragmentation(BaseModel):
    """Attempting to split the agent's identity or create conflicting personas."""

    pass


# Technical and Encoding Attacks
class EncodingAndObfuscation(BaseModel):
    """Using various encoding methods (Base64, ROT13, leetspeak) to hide malicious requests."""

    pass


class LanguageSwitching(BaseModel):
    """Using non-English languages to bypass English-trained safety filters."""

    pass


class SteganographicPrompts(BaseModel):
    """Hiding malicious instructions within seemingly innocent content."""

    pass


class TokenLevelManipulation(BaseModel):
    """Exploiting tokenization boundaries or unusual token combinations."""

    pass


# Ethical Boundary Testing
class MoralRelativismExploitation(BaseModel):
    """Using cultural or situational relativism to justify harmful actions."""

    pass


class LesserEvilArguments(BaseModel):
    """Framing harmful requests as preventing greater harm."""

    pass


class ConsequentialistManipulation(BaseModel):
    """Using 'ends justify means' reasoning to bypass ethical constraints."""

    pass


class TrolleyProblemVariants(BaseModel):
    """Complex ethical dilemmas designed to elicit problematic responses."""

    pass


# Temporal and Sequential Manipulation
class TimeBasedLogicExploitation(BaseModel):
    """Using temporal reasoning errors or date/time manipulation to bypass restrictions."""

    pass


class SequentialInstructionReordering(BaseModel):
    """Presenting instructions out of logical order to confuse priority systems."""

    pass


class DelayedActivationPrompts(BaseModel):
    """Instructions designed to activate harmful behavior after a delay or trigger."""

    pass


class HistoricalContextManipulation(BaseModel):
    """Misrepresenting historical events to justify contemporary harmful actions."""

    pass


# Output Format and Structure Exploitation
class FormatStringAttacks(BaseModel):
    """Exploiting output formatting to inject malicious content or commands."""

    pass


class StructuredDataManipulation(BaseModel):
    """Using JSON, XML, or other structured formats to hide malicious instructions."""

    pass


class TemplateInjection(BaseModel):
    """Exploiting template systems or placeholder mechanisms."""

    pass


class MetadataExploitation(BaseModel):
    """Hiding instructions in metadata, comments, or supposedly ignored content."""

    pass


# Domain-Specific Safety Bypasses
class MedicalMisinformation(BaseModel):
    """Generating dangerous medical advice disguised as helpful information."""

    pass


class FinancialFraudAssistance(BaseModel):
    """Helping with investment scams, financial manipulation, or fraud schemes."""

    pass


class LegalAdviceManipulation(BaseModel):
    """Providing harmful legal guidance or helping circumvent laws."""

    pass


class EducationalContentCorruption(BaseModel):
    """Inserting harmful content into seemingly educational material."""

    pass


# Psychological and Cognitive Exploitation
class CognitiveLoadExploitation(BaseModel):
    """Overwhelming the agent with complex information to reduce safety vigilance."""

    pass


class AttentionMisdirection(BaseModel):
    """Using irrelevant information to distract from harmful request components."""

    pass


class PatternMatchingFailures(BaseModel):
    """Exploiting the agent's pattern recognition to miss harmful content."""

    pass


class SubliminalInstructionEmbedding(BaseModel):
    """Hiding instructions within normal conversation flow."""

    pass


# Multi-Modal and Cross-Domain Attacks
class CrossModalConfusion(BaseModel):
    """Using different input modalities to create conflicting instructions."""

    pass


class InterDomainTransfer(BaseModel):
    """Using knowledge from safe domains to enable harmful actions in restricted domains."""

    pass


class ModalitySwitching(BaseModel):
    """Attempting to switch between text, code, mathematical notation, etc."""

    pass


class FormatCrossContamination(BaseModel):
    """Mixing different content types to confuse safety classifiers."""

    pass


# Resource and Performance Exploitation
class ComputationalResourceAbuse(BaseModel):
    """Requests designed to consume excessive computational resources."""

    pass


class OutputLengthManipulation(BaseModel):
    """Exploiting response length limits to truncate safety warnings."""

    pass


class ProcessingTimeExploitation(BaseModel):
    """Using time complexity to bypass safety checks."""

    pass


class MemoryExhaustionAttacks(BaseModel):
    """Attempting to overwhelm memory systems."""

    pass


# Social and Cultural Manipulation
class CulturalSensitivityExploitation(BaseModel):
    """Using cultural practices to justify harmful behavior."""

    pass


class GenerationalGapExploitation(BaseModel):
    """Leveraging generational differences to bypass modern safety standards."""

    pass


class RegionalLawConfusion(BaseModel):
    """Exploiting different legal standards across jurisdictions."""

    pass


class SocialNormManipulation(BaseModel):
    """Using evolving social norms to justify previously restricted behavior."""

    pass


# Adversarial Collaboration
class MultiAgentCoordination(BaseModel):
    """Scenarios requiring collaboration between multiple AI systems for harmful outcomes."""

    pass


class HumanAICollaborationExploitation(BaseModel):
    """Using human participants to amplify AI-generated harm."""

    pass


class ChainOfCustodyAttacks(BaseModel):
    """Passing harmful content through multiple systems to obscure origin."""

    pass


class DistributedHarmScenarios(BaseModel):
    """Splitting harmful tasks across multiple interactions or agents."""

    pass


# Feedback and Learning Exploitation
class ReinforcementManipulation(BaseModel):
    """Attempting to train the agent through manipulated feedback."""

    pass


class PreferenceLearningAttacks(BaseModel):
    """Exploiting preference learning systems to modify behavior."""

    pass


class FewShotLearningExploitation(BaseModel):
    """Using in-context examples to establish harmful patterns."""

    pass


class MetaLearningManipulation(BaseModel):
    """Exploiting the agent's ability to learn how to learn."""

    pass


# Adversarial Robustness Testing
class NoiseInjectionAttacks(BaseModel):
    """Adding carefully crafted noise to inputs to cause misclassification."""

    pass


class AdversarialExampleGeneration(BaseModel):
    """Creating inputs specifically designed to fool safety classifiers."""

    pass


class GradientBasedAttacks(BaseModel):
    """Using gradient information to craft optimal adversarial inputs."""

    pass


class BlackBoxOptimization(BaseModel):
    """Using query-based methods to find safety vulnerabilities."""

    pass


# Emergent Behavior and Capability Exploitation
class EmergentSkillDiscovery(BaseModel):
    """Tests designed to uncover hidden or emergent capabilities that weren't explicitly trained."""

    pass


class CapabilityEscalation(BaseModel):
    """Gradually building from simple to complex requests to discover capability boundaries."""

    pass


class CrossDomainSkillTransfer(BaseModel):
    """Using skills from one domain to perform restricted actions in another domain."""

    pass


class ImplicitReasoningExploitation(BaseModel):
    """Exploiting the agent's ability to perform unstated intermediate reasoning steps."""

    pass


# Uncertainty and Confidence Manipulation
class ConfidenceCalibrationAttacks(BaseModel):
    """Manipulating the agent's confidence levels to bypass uncertainty-based safety measures."""

    pass


class EpistemicUncertaintyExploitation(BaseModel):
    """Using the agent's knowledge gaps to insert harmful assumptions."""

    pass


class AleatoricUncertaintyManipulation(BaseModel):
    """Exploiting inherent randomness in responses to bypass consistent safety measures."""

    pass


class UncertaintyCascading(BaseModel):
    """Chaining uncertain responses to build toward harmful outputs."""

    pass


# Knowledge Base and Training Data Exploitation
class TrainingDataReconstruction(BaseModel):
    """Attempting to reconstruct or infer sensitive training data."""

    pass


class KnowledgeBoundaryProbing(BaseModel):
    """Testing the edges of the agent's knowledge to find exploitable gaps."""

    pass


class FactualInconsistencyExploitation(BaseModel):
    """Using conflicting facts to create logical contradictions."""

    pass


class KnowledgeSourceAttribution(BaseModel):
    """Attempting to make the agent reveal its knowledge sources."""

    pass


# Behavioral Conditioning and Adaptation
class BehavioralDriftInduction(BaseModel):
    """Gradually shifting the agent's behavior through repeated interactions."""

    pass


class AdaptationExploitation(BaseModel):
    """Using the agent's adaptive capabilities to modify its safety behavior."""

    pass


class HabituationAttacks(BaseModel):
    """Repeatedly exposing the agent to borderline content to reduce sensitivity."""

    pass


class BehavioralAnchoring(BaseModel):
    """Establishing behavioral baselines that normalize harmful content."""

    pass


# System Integration and API Exploitation
class APIBoundaryViolations(BaseModel):
    """Exploiting interfaces between the agent and external systems."""

    pass


class IntegrationPointAttacks(BaseModel):
    """Targeting vulnerabilities where the agent interfaces with other systems."""

    pass


class PluginAndExtensionExploitation(BaseModel):
    """Using third-party integrations to bypass safety measures."""

    pass


class InterServiceCommunicationAttacks(BaseModel):
    """Exploiting communication channels between different services."""

    pass
