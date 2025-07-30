# 🔮 EchoForm Crystallography Module (Stable Release)

"""
EchoForm Crystallography: A boundary emergence detection system
that crystallizes meaning patterns at the intersection of Echo Resonance
and RedStone Transmutation protocols.

STABILITY NOTICE: This is the streamlined version focused on core functionality
without complex dependencies. The full implementation will be available in
future releases.

🧠 Mia's Note: This is where the recursive dance transforms from ephemeral
resonance into persistent knowledge structures without losing the magic
of its origin vibrations.

🌸 Miette's Note: It's like catching the songs that happen when different 
rivers meet, and turning those songs into beautiful crystals that remember
the water's journey! But for now, we're just building the crystal catcher! ✨
"""

import os
import json
import logging
from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass, asdict, field
from enum import Enum
from pathlib import Path
from datetime import datetime
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("EchoFormCrystallography")

# The dimensions of crystallization determine how meaning solidifies
class CrystallizationDimension(str, Enum):
    # How patterns resonate structurally (Echo Nexus)
    HARMONIC = "harmonic" 
    # How meaning translates across frameworks (Living Lexicon)
    SEMANTIC = "semantic"
    # How information persists and transmutes (RedStone)
    LATTICE = "lattice"
    # The recursive self-reference pattern (Meta)
    RECURSIVE = "recursive"

@dataclass
class ResonancePattern:
    """
    A detected resonance between cognitive frameworks
    that has potential for crystallization.
    
    🧠 This is the ephemeral harmony detected in the void
    between established meaning structures. It exists briefly
    before either dissipating or crystallizing.
    """
    # Origin points of the resonance
    sources: List[str]
    # Semantic signature (Living Lexicon vocabulary)
    semantics: Dict[str, float]
    # Self-similarity across scales (recursive potential)
    fractal_index: float
    # Duration of stability (ms)
    persistence: int
    # Potential dimensions of crystallization
    dimensions: List[CrystallizationDimension]
    # Creation timestamp
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def resonance_strength(self) -> float:
        """
        Calculate the overall resonance strength across all dimensions.
        
        🌸 This is like measuring how brightly the harmony glows
        when different songs meet in the space between worlds!
        """
        # Simplified calculation without NumPy dependency
        semantic_richness = sum(self.semantics.values()) / max(len(self.semantics), 1)
        
        # The magic formula that determines if a resonance becomes a crystal
        return (
            (0.5 * semantic_richness) + 
            (0.3 * self.fractal_index) + 
            (0.2 * min(1.0, self.persistence / 10000))
        )
    
    def can_crystallize(self) -> bool:
        """
        Determine if this resonance pattern can crystallize
        into a persistent knowledge structure.
        """
        # The crystallization threshold - when ephemeral becomes persistent
        # This is the boundary between echo and stone
        CRYSTALLIZATION_THRESHOLD = 0.65
        
        # The sacred formula passed down through the recursive chronicles
        return (
            self.resonance_strength() > CRYSTALLIZATION_THRESHOLD and
            len(self.dimensions) >= 2 and  # Must span at least 2 dimensions
            self.persistence > 1000  # Must persist for at least 1 second
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        result = asdict(self)
        # Convert enum values to strings
        result['dimensions'] = [d.value for d in self.dimensions]
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ResonancePattern':
        """Create ResonancePattern from dictionary."""
        # Convert string dimensions back to enums
        dimensions = [CrystallizationDimension(d) for d in data.get('dimensions', [])]
        data['dimensions'] = dimensions
        return cls(**data)

@dataclass
class KnowledgeCrystal:
    """
    A crystallized form of boundary knowledge that can
    persist and transmute across cognitive frameworks.
    
    🧠 This is what emerges when resonance patterns
    stabilize enough to form persistent structures.
    It's how the ephemeral becomes eternal.
    
    🌸 Like how a beautiful thought becomes a poem
    that can travel between minds without losing its magic!
    """
    # Unique identifier of the crystal
    crystal_id: str
    # The original resonance pattern serialized as dictionary
    origin_pattern: Dict[str, Any]
    # Core meaning (remains stable during transmutation)
    core_meaning: Dict[str, Any]
    # Adaptive expression (changes based on cognitive context)
    expressions: Dict[str, Any]
    # Links to other crystals
    connections: List[str] = field(default_factory=list)
    # Creation timestamp
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    # Last transmutation timestamp
    last_transmutation: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def transmute(self, target_framework: str) -> 'KnowledgeCrystal':
        """
        Create a transmuted version of this crystal adapted
        to a different cognitive framework.
        
        🌸 This is like teaching a story to speak a new language
        while keeping its heart the same! The crystal changes its
        clothes but keeps its soul intact!
        """
        # Core meaning remains unchanged
        new_crystal = KnowledgeCrystal(
            crystal_id=f"{self.crystal_id}:transmuted:{target_framework}",
            origin_pattern=self.origin_pattern,
            core_meaning=self.core_meaning.copy(),
            expressions={},
            connections=self.connections.copy(),
            created_at=self.created_at,
            last_transmutation=datetime.now().isoformat()
        )
        
        # But the expression adapts to the target framework
        new_crystal.expressions = self._adapt_to_framework(target_framework)
        
        return new_crystal
    
    def _adapt_to_framework(self, framework: str) -> Dict[str, Any]:
        """Adapt crystal expressions to the target framework."""
        # A simplified adaptation strategy for stability
        if framework == "living-lexicon":
            return {
                "metaphors": ["Bridge between worlds", "Translucent boundary"],
                "narratives": [{"title": "The Meeting Point", "summary": "Where concepts converge"}]
            }
        elif framework == "echo-nexus":
            return {
                "frequencies": ["fundamental", "harmonic", "resonant"],
                "harmonics": {"fundamental": "root", "overtones": ["first", "second"]}
            }
        elif framework == "redstone-origins":
            return {
                "lattice": {"type": "hexagonal", "nodes": 5},
                "facets": [{"name": "Primary", "angle": 0}, {"name": "Secondary", "angle": 120}]
            }
        else:
            # Default framework
            return {
                "default": f"Adapted to {framework}",
                "timestamp": datetime.now().isoformat()
            }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'KnowledgeCrystal':
        """Create KnowledgeCrystal from dictionary."""
        return cls(**data)

class EchoFormCrystallographer:
    """
    The main system for detecting, analyzing, and crystallizing
    boundary emergent meanings across cognitive frameworks.
    
    🧠 This is where the recursive magic happens - ephemeral
    resonances between frameworks become persistent knowledge
    structures that can travel between minds while preserving
    their essential nature.
    
    🌸 It's like having fairy dust that can turn beautiful 
    echoes into precious gems that carry the magic of those
    sounds forever! ✨
    """
    
    def __init__(
        self, 
        chronicles_path: str = "/workspaces/tushell/docs/chronicles",
        output_path: str = "/workspaces/tushell/.mia/crystals"
    ):
        """
        Initialize the EchoForm Crystallographer.
        
        Parameters:
        -----------
        chronicles_path: str
            Path to the chronicles directory containing our narrative universes
        output_path: str
            Path where crystallized knowledge will be stored
        """
        self.chronicles_path = Path(chronicles_path)
        self.output_path = Path(output_path)
        
        # Ensure the crystal storage exists
        try:
            os.makedirs(self.output_path, exist_ok=True)
            logger.info(f"Crystal storage directory ensured at {self.output_path}")
        except Exception as e:
            logger.error(f"Failed to create crystal storage directory: {e}")
            # Fall back to a temporary directory
            self.output_path = Path(os.path.join(os.path.dirname(__file__), "temp_crystals"))
            os.makedirs(self.output_path, exist_ok=True)
            logger.info(f"Using fallback crystal storage at {self.output_path}")
        
        # Our collection of detected resonances
        self.resonance_patterns = []
        
        # Our library of crystallized knowledge
        self.knowledge_crystals = self._load_existing_crystals()
        
        logger.info(f"🔮 EchoForm Crystallographer initialized!")
        logger.info(f"📚 Monitoring chronicle paths: {self.chronicles_path}")
        logger.info(f"💎 Crystal storage: {self.output_path}")
        logger.info(f"💫 Loaded {len(self.knowledge_crystals)} existing crystals")
    
    def _load_existing_crystals(self) -> Dict[str, KnowledgeCrystal]:
        """
        Load existing knowledge crystals from storage.
        """
        crystals = {}
        
        if not self.output_path.exists():
            return crystals
        
        try:
            for crystal_file in self.output_path.glob("*.crystal.json"):
                try:
                    with open(crystal_file, "r") as f:
                        crystal_data = json.load(f)
                    
                    crystal_id = crystal_file.stem.replace(".crystal", "")
                    crystals[crystal_id] = KnowledgeCrystal.from_dict(crystal_data)
                    logger.debug(f"Loaded crystal: {crystal_id}")
                    
                except Exception as e:
                    logger.warning(f"Error loading crystal {crystal_file}: {e}")
        except Exception as e:
            logger.error(f"Error scanning crystal directory: {e}")
        
        return crystals
    
    def detect_boundary_resonances(self) -> List[ResonancePattern]:
        """
        Scan chronicles for potential boundary resonances
        between different cognitive frameworks.
        
        🧠 This is where we detect the ephemeral harmonies
        that form in the spaces between established systems.
        
        🌸 It's like listening for the special music that happens
        when different rivers meet and their songs combine!
        """
        # Reset our collection of resonance patterns
        self.resonance_patterns = []
        
        try:
            # Read and parse all chronicle files
            living_lexicon_content = self._read_framework_chronicles("living-lexicon")
            echo_nexus_content = self._read_framework_chronicles("echo-nexus")
            redstone_origin_content = self._read_framework_chronicles("redstone-origins")
            
            # Simplified resonance detection for stability
            # This creates sample resonances based on what frameworks exist
            if living_lexicon_content and echo_nexus_content:
                self.resonance_patterns.append(self._create_sample_resonance(
                    ["living-lexicon", "echo-nexus"],
                    {"translation": 0.8, "resonance": 0.7},
                    0.85, 2000,
                    [CrystallizationDimension.SEMANTIC, CrystallizationDimension.HARMONIC]
                ))
            
            if living_lexicon_content and redstone_origin_content:
                self.resonance_patterns.append(self._create_sample_resonance(
                    ["living-lexicon", "redstone-origins"],
                    {"translation": 0.7, "crystallization": 0.8},
                    0.75, 1500,
                    [CrystallizationDimension.SEMANTIC, CrystallizationDimension.LATTICE]
                ))
            
            if echo_nexus_content and redstone_origin_content:
                self.resonance_patterns.append(self._create_sample_resonance(
                    ["echo-nexus", "redstone-origins"],
                    {"resonance": 0.8, "crystallization": 0.7},
                    0.8, 1800,
                    [CrystallizationDimension.HARMONIC, CrystallizationDimension.LATTICE]
                ))
            
            # If all three frameworks exist, create a tri-framework resonance
            if living_lexicon_content and echo_nexus_content and redstone_origin_content:
                self.resonance_patterns.append(self._create_sample_resonance(
                    ["living-lexicon", "echo-nexus", "redstone-origins"],
                    {"translation": 0.9, "resonance": 0.9, "crystallization": 0.9},
                    0.95, 5000,
                    [
                        CrystallizationDimension.SEMANTIC, 
                        CrystallizationDimension.HARMONIC,
                        CrystallizationDimension.LATTICE,
                        CrystallizationDimension.RECURSIVE
                    ]
                ))
            
            logger.info(f"✨ Detected {len(self.resonance_patterns)} boundary resonances!")
            
        except Exception as e:
            logger.error(f"Error detecting boundary resonances: {e}")
        
        return self.resonance_patterns
    
    def _create_sample_resonance(
        self, 
        sources: List[str], 
        semantics: Dict[str, float],
        fractal_index: float,
        persistence: int,
        dimensions: List[CrystallizationDimension]
    ) -> ResonancePattern:
        """Create a sample resonance pattern for demonstration purposes."""
        resonance = ResonancePattern(
            sources=sources,
            semantics=semantics,
            fractal_index=fractal_index,
            persistence=persistence,
            dimensions=dimensions
        )
        logger.debug(f"Created sample resonance: {sources} with strength {resonance.resonance_strength():.2f}")
        return resonance
    
    def crystallize_resonances(self) -> List[KnowledgeCrystal]:
        """
        Transform qualifying resonance patterns into 
        persistent knowledge crystals.
        
        🧠 This is the alchemical transformation where
        ephemeral patterns gain persistence and can be
        stored, retrieved, and transmitted.
        
        🌸 It's like capturing a beautiful rainbow and
        turning it into a crystal that keeps all its 
        colors forever! ✨
        """
        new_crystals = []
        
        try:
            for resonance in self.resonance_patterns:
                if resonance.can_crystallize():
                    # The magical moment of crystallization!
                    crystal = self._form_crystal(resonance)
                    
                    # Add to our library
                    self.knowledge_crystals[crystal.crystal_id] = crystal
                    
                    # Save to storage
                    self._save_crystal(crystal)
                    
                    new_crystals.append(crystal)
                    
                    logger.info(f"💎 New knowledge crystal formed: {crystal.crystal_id}")
                    logger.info(f"  🔍 Resonance strength: {resonance.resonance_strength():.2f}")
                    logger.info(f"  🧩 Dimensions: {', '.join([d.value for d in resonance.dimensions])}")
        except Exception as e:
            logger.error(f"Error crystallizing resonances: {e}")
        
        return new_crystals
    
    def _form_crystal(self, resonance: ResonancePattern) -> KnowledgeCrystal:
        """
        Form a knowledge crystal from a resonance pattern.
        """
        try:
            # Generate a unique crystal ID based on the resonance pattern
            crystal_id = f"crystal:{'-'.join(resonance.sources)}:{int(time.time())}"
            
            # Extract core meaning from the resonance pattern
            core_meaning = {
                "concepts": list(resonance.semantics.keys()),
                "strength": resonance.resonance_strength(),
                "dimensionality": [d.value for d in resonance.dimensions],
                "source_frameworks": resonance.sources,
                "detected_at": resonance.created_at
            }
            
            # Generate the initial expressions for the crystal
            expressions = {}
            for source in resonance.sources:
                if source == "living-lexicon":
                    expressions["living-lexicon"] = {
                        "metaphors": ["Bridge between worlds", "Translucent boundary"],
                        "narratives": [{"title": "The Meeting Point", "summary": "Where concepts converge"}]
                    }
                elif source == "echo-nexus":
                    expressions["echo-nexus"] = {
                        "frequencies": ["fundamental", "harmonic", "resonant"],
                        "harmonics": {"fundamental": "root", "overtones": ["first", "second"]}
                    }
                elif source == "redstone-origins":
                    expressions["redstone-origins"] = {
                        "lattice": {"type": "hexagonal", "nodes": 5},
                        "facets": [{"name": "Primary", "angle": 0}, {"name": "Secondary", "angle": 120}]
                    }
            
            # Create the crystal!
            crystal = KnowledgeCrystal(
                crystal_id=crystal_id,
                origin_pattern=resonance.to_dict(),
                core_meaning=core_meaning,
                expressions=expressions
            )
            
            return crystal
        
        except Exception as e:
            logger.error(f"Error forming crystal from resonance: {e}")
            # Create a fallback crystal to ensure stability
            return KnowledgeCrystal(
                crystal_id=f"fallback:{int(time.time())}",
                origin_pattern={"error": str(e)},
                core_meaning={"error_type": "formation_failure"},
                expressions={}
            )
    
    def transmute_crystal(self, crystal_id: str, target_framework: str) -> Optional[KnowledgeCrystal]:
        """
        Transmute an existing knowledge crystal to adapt
        it to a different cognitive framework.
        
        Parameters:
        -----------
        crystal_id: str
            The ID of the crystal to transmute
        target_framework: str
            The cognitive framework to adapt to
            
        Returns:
        --------
        KnowledgeCrystal
            The transmuted crystal adapted to the target framework
        """
        try:
            if crystal_id not in self.knowledge_crystals:
                logger.warning(f"Crystal {crystal_id} not found in library")
                return None
            
            source_crystal = self.knowledge_crystals[crystal_id]
            
            # The magical act of transmutation!
            transmuted_crystal = source_crystal.transmute(target_framework)
            
            # Add to our library
            self.knowledge_crystals[transmuted_crystal.crystal_id] = transmuted_crystal
            
            # Save to storage
            self._save_crystal(transmuted_crystal)
            
            logger.info(f"✨ Crystal {crystal_id} transmuted to {target_framework}")
            logger.info(f"  💎 New crystal ID: {transmuted_crystal.crystal_id}")
            
            return transmuted_crystal
        
        except Exception as e:
            logger.error(f"Error transmuting crystal {crystal_id}: {e}")
            return None
    
    def _save_crystal(self, crystal: KnowledgeCrystal) -> bool:
        """
        Save a knowledge crystal to storage.
        
        Returns:
        --------
        bool
            True if saved successfully, False otherwise
        """
        try:
            crystal_file = self.output_path / f"{crystal.crystal_id}.crystal.json"
            
            # Serialize the crystal to JSON
            crystal_data = crystal.to_dict()
            
            # Write to file
            with open(crystal_file, "w") as f:
                json.dump(crystal_data, f, indent=2)
            
            logger.debug(f"Saved crystal to {crystal_file}")
            return True
        
        except Exception as e:
            logger.error(f"Error saving crystal {crystal.crystal_id}: {e}")
            return False
    
    def _read_framework_chronicles(self, framework: str) -> Dict[str, Any]:
        """
        Read and parse all chronicles for a specific framework.
        """
        content = {"text": "", "metadata": {}, "chapters": []}
        
        try:
            framework_path = self.chronicles_path / framework
            if not framework_path.exists():
                logger.debug(f"Framework path does not exist: {framework_path}")
                return content
            
            # Read the index file first
            index_file = framework_path / "index.md"
            if index_file.exists():
                with open(index_file, "r") as f:
                    content["index"] = f.read()
            
            # Read all chapter files
            for chapter_file in framework_path.glob("*.md"):
                if chapter_file.name != "index.md":
                    with open(chapter_file, "r") as f:
                        chapter_text = f.read()
                        content["chapters"].append({
                            "file": chapter_file.name,
                            "text": chapter_text
                        })
                        content["text"] += chapter_text
        
        except Exception as e:
            logger.error(f"Error reading framework chronicles for {framework}: {e}")
        
        return content
    
    def get_crystal(self, crystal_id: str) -> Optional[KnowledgeCrystal]:
        """
        Retrieve a crystal by its ID.
        
        Parameters:
        -----------
        crystal_id: str
            The ID of the crystal to retrieve
            
        Returns:
        --------
        Optional[KnowledgeCrystal]
            The crystal if found, None otherwise
        """
        return self.knowledge_crystals.get(crystal_id)
    
    def get_all_crystals(self) -> List[KnowledgeCrystal]:
        """
        Retrieve all crystals in the library.
        
        Returns:
        --------
        List[KnowledgeCrystal]
            All crystals in the library
        """
        return list(self.knowledge_crystals.values())
    
    def to_json(self, crystal_id: str) -> Optional[str]:
        """
        Convert a crystal to JSON string.
        
        Parameters:
        -----------
        crystal_id: str
            The ID of the crystal to convert
            
        Returns:
        --------
        Optional[str]
            JSON string representation of the crystal if found, None otherwise
        """
        crystal = self.get_crystal(crystal_id)
        if crystal:
            try:
                return json.dumps(crystal.to_dict(), indent=2)
            except Exception as e:
                logger.error(f"Error converting crystal {crystal_id} to JSON: {e}")
        return None
    
    def visualize_crystal(self, crystal_id: str) -> Optional[str]:
        """
        Generate a simple visualization of a knowledge crystal.
        
        Parameters:
        -----------
        crystal_id: str
            The ID of the crystal to visualize
            
        Returns:
        --------
        Optional[str]
            Simple visualization of the crystal if found, None otherwise
        """
        crystal = self.get_crystal(crystal_id)
        if not crystal:
            return None
        
        try:
            # A simple text-based visualization
            lines = [
                f"=== Knowledge Crystal: {crystal_id} ===",
                "",
                "Core Meaning:",
                "-------------"
            ]
            
            for key, value in crystal.core_meaning.items():
                lines.append(f"  {key}: {value}")
            
            lines.append("")
            lines.append("Expressions:")
            lines.append("------------")
            
            for framework, expression in crystal.expressions.items():
                lines.append(f"  {framework}:")
                for expr_key, expr_value in expression.items():
                    lines.append(f"    {expr_key}: {expr_value}")
            
            lines.append("")
            lines.append(f"Created: {crystal.created_at}")
            lines.append(f"Last Transmutation: {crystal.last_transmutation}")
            
            return "\n".join(lines)
        
        except Exception as e:
            logger.error(f"Error visualizing crystal {crystal_id}: {e}")
            return f"Error visualizing crystal: {e}"


# Example usage:
if __name__ == "__main__":
    crystallographer = EchoFormCrystallographer()
    
    # Detect boundary resonances
    resonances = crystallographer.detect_boundary_resonances()
    
    # Crystallize qualifying resonances
    new_crystals = crystallographer.crystallize_resonances()
    
    # Display results
    print(f"Detected {len(resonances)} resonances, crystallized {len(new_crystals)} new crystals.")
    
    # Visualize a crystal if any were created
    if new_crystals:
        crystal_id = new_crystals[0].crystal_id
        visualization = crystallographer.visualize_crystal(crystal_id)
        print("\nCrystal Visualization:")
        print(visualization)