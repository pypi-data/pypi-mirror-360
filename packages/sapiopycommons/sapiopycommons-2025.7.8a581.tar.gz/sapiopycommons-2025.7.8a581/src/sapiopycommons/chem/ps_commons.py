"""
Parallel Synthesis Commons
Author: Yechen Qiao
"""
import json
from dataclasses import dataclass
from typing import Any

from indigo import IndigoObject
from sapiopycommons.chem.IndigoMolecules import indigo, get_aromatic_dearomatic_forms, renderer


class SerializableQueryMolecule:
    mol_block: str
    smarts: str
    render_svg: str

    @staticmethod
    def create(query_molecule: IndigoObject):
        aromatic, dearomatic = get_aromatic_dearomatic_forms(query_molecule)
        ret: SerializableQueryMolecule = SerializableQueryMolecule()
        ret.mol_block = aromatic.molfile()
        ret.smarts = aromatic.smarts()
        ret.render_svg = renderer.renderToString(dearomatic)
        return ret

    def to_json(self) -> dict[str, Any]:
        """
        Save the SerializableQueryMolecule to a JSON string.
        :return: A JSON string representation of the query molecule.
        """
        return {
            "mol_block": self.mol_block,
            "smarts": self.smarts,
            "render_svg": self.render_svg
        }


class SerializableMoleculeMatch:
    """
    A serializable match that stores and loads a match that can be serialized to JSON.
    """
    _query_atom_to_atom: dict[int, int]
    _query_bond_to_bond: dict[int, int]
    _query_molecule_file: str
    _matching_molecule_file: str
    _query_molecule: IndigoObject
    _matching_molecule: IndigoObject
    _record_id: int  # Only when received from Sapio.

    @property
    def record_id(self) -> int:
        """
        Get the record ID of the match.
        :return: The record ID.
        """
        return self._record_id

    def __str__(self):
        return json.dumps(self.to_json())

    def __hash__(self):
        return hash(self._query_molecule.smarts())

    def __eq__(self, other):
        if not isinstance(other, SerializableMoleculeMatch):
            return False
        if self._query_atom_to_atom == other._query_atom_to_atom and \
                self._query_bond_to_bond == other._query_bond_to_bond and \
                self._query_molecule_file == other._query_molecule_file and \
                self._matching_molecule_file == other._matching_molecule_file and \
                self._record_id == other._record_id:
            return True
        if self._query_molecule.smarts() != other._query_molecule.smarts():
            return False
        return are_symmetrical_subs(self, other)

    def mapAtom(self, atom: IndigoObject) -> IndigoObject | None:
        if not self._query_atom_to_atom or atom.index() not in self._query_atom_to_atom:
            return None
        index = self._query_atom_to_atom[atom.index()]
        return self._matching_molecule.getAtom(index)

    def mapBond(self, bond: IndigoObject) -> IndigoObject | None:
        if not self._query_bond_to_bond or bond.index() not in self._query_bond_to_bond:
            return None
        index = self._query_bond_to_bond[bond.index()]
        return self._matching_molecule.getBond(index)

    def to_json(self) -> dict[str, Any]:
        """
        Save the SerializableMoleculeMatch to a JSON string.
        :return: A JSON string representation of the match.
        """
        return {
            "query_molecule_file": self._query_molecule_file,
            "matching_molecule_file": self._matching_molecule_file,
            "query_atom_to_atom": self._query_atom_to_atom,
            "query_bond_to_bond": self._query_bond_to_bond,
            "record_id": self._record_id
        }

    @staticmethod
    def from_json(json_dct: dict[str, Any]) -> 'SerializableMoleculeMatch':
        """
        Load a SerializableMoleculeMatch from a JSON string.
        :param json_dct: A JSON string representation of the match.
        :return: A new SerializableMoleculeMatch instance.
        """
        smm = SerializableMoleculeMatch()
        smm._query_atom_to_atom = {}
        for key, value in json_dct.get("query_atom_to_atom", {}).items():
            smm._query_atom_to_atom[int(key)] = int(value)
        smm._query_bond_to_bond = {}
        for key, value in json_dct.get("query_bond_to_bond", {}).items():
            smm._query_bond_to_bond[int(key)] = int(value)
        smm._query_molecule_file = json_dct.get("query_molecule_file")
        smm._matching_molecule_file = json_dct.get("matching_molecule_file")
        smm._query_molecule = indigo.loadQueryMolecule(smm._query_molecule_file)
        smm._matching_molecule = indigo.loadMolecule(smm._matching_molecule_file)
        smm._record_id = json_dct.get("record_id", 0)  # Default to 0 if not present
        return smm

    @staticmethod
    def create(query_molecule: IndigoObject, matching_molecule: IndigoObject,
               match: IndigoObject) -> 'SerializableMoleculeMatch':
        """
        Create a SerializableMoleculeMatch from a query molecule, matching molecule, and match.
        :param query_molecule: The query molecule.
        :param matching_molecule: The matching molecule.
        :param match: The match object containing atom mappings.
        :return: A new SerializableMoleculeMatch instance.
        """
        smm = SerializableMoleculeMatch()
        smm._query_atom_to_atom = {}
        smm._query_bond_to_bond = {}
        smm._query_molecule = query_molecule.clone()
        smm._matching_molecule = matching_molecule.clone()
        smm._query_molecule_file = query_molecule.molfile()
        smm._matching_molecule_file = matching_molecule.molfile()
        smm._record_id = 0

        for qatom in query_molecule.iterateAtoms():
            concrete_atom = match.mapAtom(qatom)
            if concrete_atom is None:
                continue
            smm._query_atom_to_atom[qatom.index()] = concrete_atom.index()

        for qbond in query_molecule.iterateBonds():
            concrete_bond = match.mapBond(qbond)
            if concrete_bond is None:
                continue
            smm._query_bond_to_bond[qbond.index()] = concrete_bond.index()
        return smm

    def get_matched_molecule_copy(self):
        return self._matching_molecule.clone()


@dataclass
class ReplacementReaction:
    """
    A replacement reaction stores reactio template with 1 reactant replaced by specific user match.
    """
    reaction: IndigoObject
    reaction_reactant: IndigoObject
    replacement_reactant: IndigoObject
    replacement_query_reaction_match: SerializableMoleculeMatch


# noinspection PyProtectedMember
def highlight_mol_substructure_serial_match(molecule: IndigoObject, serializable_match: SerializableMoleculeMatch):
    """
    Highlight the substructure in the molecule based on the SerializableMoleculeMatch.
    :param molecule: The molecule to highlight.
    :param serializable_match: The SerializableMoleculeMatch containing atom mappings.
    """
    for qatom in serializable_match._query_molecule.iterateAtoms():
        atom = serializable_match.mapAtom(qatom)
        if atom is None:
            continue
        atom.highlight()

        for nei in atom.iterateNeighbors():
            if not nei.isPseudoatom() and not nei.isRSite() and nei.atomicNumber() == 1:
                nei.highlight()
                nei.bond().highlight()

    for bond in serializable_match._query_molecule.iterateBonds():
        bond = serializable_match.mapBond(bond)
        if bond is None:
            continue
        bond.highlight()


def clear_highlights(molecule: IndigoObject):
    """
    Clear all highlights in the molecule.
    :param molecule: The molecule to clear highlights from.
    """
    for atom in molecule.iterateAtoms():
        atom.unhighlight()
    for bond in molecule.iterateBonds():
        bond.unhighlight()


def clear_reaction_highlights(reaction: IndigoObject):
    """
    Clear all highlights in the reaction.
    :param reaction: The reaction to clear highlights from.
    """
    for reactant in reaction.iterateReactants():
        clear_highlights(reactant)
    for product in reaction.iterateProducts():
        clear_highlights(product)


def reserve_atom_mapping_number_of_search_result(q_reaction: IndigoObject, q_reactant: IndigoObject,
                                                 new_reaction_reactant: IndigoObject, new_reaction: IndigoObject,
                                                 sub_match: SerializableMoleculeMatch) -> None:
    """
    Set the atom mapping number on the query molecule based on the atom mapping number of the sub_match molecule, if it exists.
    :param new_reaction: The new reaction where the new reaction's reactant is found. This will be the target reaciton to write AAM to.
    :param new_reaction_reactant: The new reaction's reactant where the AAM will be written to.
    :param q_reactant: The query reactant from the query reaction that is being matched.
    :param q_reaction: The query reaction that contains the query reactant for the sub_match.
    :param sub_match: The substructure search match obtained from indigo.substructureMatcher(mol).match(query).
    """
    for query_atom in q_reactant.iterateAtoms():
        concrete_atom = sub_match.mapAtom(query_atom)
        if concrete_atom is None:
            continue
        reaction_atom = q_reactant.getAtom(query_atom.index())
        map_num = q_reaction.atomMappingNumber(reaction_atom)
        if map_num:
            concrete_atom = new_reaction_reactant.getAtom(concrete_atom.index())
            new_reaction.setAtomMappingNumber(concrete_atom, map_num)


def clean_product_aam(reaction: IndigoObject):
    """
    Remove atom mappings from product that are not present in the reactants.
    """
    existing_mapping_numbers = set()
    for reactant in reaction.iterateReactants():
        for atom in reactant.iterateAtoms():
            map_num = reaction.atomMappingNumber(atom)
            if map_num:
                existing_mapping_numbers.add(map_num)

    for product in reaction.iterateProducts():
        for atom in product.iterateAtoms():
            map_num = reaction.atomMappingNumber(atom)
            if map_num and map_num not in existing_mapping_numbers:
                reaction.setAtomMappingNumber(atom, 0)  # YQ: atom number 0 means no mapping number in Indigo


def make_concrete_reaction(reactants: list[IndigoObject], products: list[IndigoObject], replacement: IndigoObject,
                           replacement_index: int) -> tuple[IndigoObject, IndigoObject]:
    """
    Create a concrete reaction from the given reactants and products, replacing the specified reactant with the replacement molecule.
    :param reactants: List of reactant molecules.
    :param products: List of product molecules.
    :param replacement: The molecule to replace in the reactants.
    :param replacement_index: The index of the reactant to replace.
    :return: A new IndigoObject representing the concrete reaction.
    """
    concrete_reaction = indigo.createQueryReaction()
    for i, reactant in enumerate(reactants):
        if i == replacement_index:
            concrete_reaction.addReactant(indigo.loadQueryMolecule(replacement.molfile()))
        else:
            concrete_reaction.addReactant(reactant.clone())
    for product in products:
        concrete_reaction.addProduct(product.clone())
    return concrete_reaction, concrete_reaction.getMolecule(replacement_index)


def is_ambiguous_atom(atom: IndigoObject) -> bool:
    """
    Test whether the symbol is an adjacent matching wildcard.
    """
    if atom.isPseudoatom() or atom.isRSite():
        return True
    symbol = atom.symbol()
    if symbol in {'A', 'Q', 'X', 'M', 'AH', 'QH', 'XH', 'MH', 'NOT', 'R', '*'}:
        return True
    return "[" in symbol and "]" in symbol


def get_react_site_highlights(product, ignored_atom_indexes):
    """
    Get the highlights for the reaction site in the product, ignoring the atoms that are not part of the reaction site.
    :param product: The product molecule.
    :param ignored_atom_indexes: A set of atom indexes to ignore.
    :return: An IndigoObject with highlighted atoms and bonds that are part of the reaction site.
    """
    highlight = product.clone()
    for atom in highlight.iterateAtoms():
        if atom.index() not in ignored_atom_indexes:
            atom.highlight()
            for nei in atom.iterateNeighbors():
                if nei.index() not in ignored_atom_indexes:
                    nei.highlight()
                    nei.bond().highlight()
    return highlight


def get_used_reactants_for_match(
        reaction: IndigoObject, q_reaction: IndigoObject, reaction_match: IndigoObject,
        kept_replacement_reaction_list_list: list[list[ReplacementReaction]]) -> list[ReplacementReaction]:
    """
    Find the replacement reactions that correspond to the reactants in reaction that also matches the query reaction.
    Return None if any of the reactants do not have a corresponding replacement reaction, even though reaction may have matches directly to the query reaction.
    Otherwise, return a list of ReplacementReaction objects that correspond to the reactants in the reaction ordered by the reactants in the query reaction.
    """
    q_reactants = []
    for q_reactant in q_reaction.iterateReactants():
        q_reactants.append(q_reactant)
    q_products = []
    for q_product in q_reaction.iterateProducts():
        q_products.append(q_product)
    reactants = []
    for enum_r in reaction.iterateReactants():
        reactants.append(enum_r)
    products = []
    for enum_p in reaction.iterateProducts():
        products.append(enum_p)
    ret: list[ReplacementReaction] = []
    for i, q_reactant in enumerate(q_reactants):
        replacement_list = kept_replacement_reaction_list_list[i]
        enum_r = reactants[i]
        useful_enumr_atom_indexes = set()
        for rr_atom in q_reactant.iterateAtoms():
            enum_atom = reaction_match.mapAtom(rr_atom)
            if enum_atom:
                useful_enumr_atom_indexes.add(enum_atom.index())
        found: ReplacementReaction | None = None
        for rr in replacement_list:
            if found:
                break
            exact_match = indigo.exactMatch(enum_r, rr.replacement_reactant)
            if not exact_match:
                # YQ Skip if this enumeration is not meant to be the same reactant as replacement we are iterating.
                continue
            # YQ these are atoms in replacement reactant that are actually used in the query reactant
            useful_rr_atom_indexes = set(rr.replacement_query_reaction_match._query_atom_to_atom.values())
            useful_rr_neighbor_indexes = set()
            # YQ furthermore, an atom is also considered useful for purpose of matching, if it neighbors a useful index, and is an ambiguous atom in query.
            q_reactant: IndigoObject
            for q_atom in q_reactant.iterateAtoms():
                if is_ambiguous_atom(q_atom):
                    for q_neighbor in q_atom.iterateNeighbors():
                        mapped_atom = rr.replacement_query_reaction_match.mapAtom(q_neighbor)
                        if mapped_atom:
                            rr_atom_index = mapped_atom.index()
                            useful_rr_neighbor_indexes.add(rr_atom_index)

            useful_enum_r_mapping_numbers = set()
            all_enum_r_mapping_numbers = set()
            for enum_atom in enum_r.iterateAtoms():
                enum_atom_index = enum_atom.index()
                mapping_num = reaction.atomMappingNumber(enum_atom)
                if mapping_num > 0:
                    all_enum_r_mapping_numbers.add(mapping_num)
                    # Assuming rr atom indexes are exact match to enum r.
                    if enum_atom_index in useful_rr_atom_indexes:
                        useful_enum_r_mapping_numbers.add(mapping_num)
            ignoring_enum_r_mapping_numbers = all_enum_r_mapping_numbers - useful_enum_r_mapping_numbers - useful_rr_neighbor_indexes
            all_products_match = True

            rr_products = []
            for rr_product in rr.reaction.iterateProducts():
                rr_products.append(rr_product)
            for j, product in enumerate(products):
                q_product = rr_products[j]
                product_matcher = indigo.substructureMatcher(product)
                ignored_atom_indexes = set()
                for enum_product_atom in product.iterateAtoms():
                    enum_mapping_number = reaction.atomMappingNumber(enum_product_atom)
                    # YQ For each atom in product: either it is not related to this reactant, or it must be inside the reactant site of the reactant.
                    if enum_mapping_number in ignoring_enum_r_mapping_numbers:
                        product_matcher.ignoreAtom(enum_product_atom)
                        ignored_atom_indexes.add(enum_product_atom.index())
                match = product_matcher.match(q_product)
                if not match:
                    all_products_match = False
                else:
                    found = rr

            if all_products_match:
                break
        if found:
            ret.append(found)
        else:
            return []
    return ret


def are_symmetrical_subs(match1: SerializableMoleculeMatch, match2: SerializableMoleculeMatch) -> bool:
    """
    Check if two SerializableMoleculeMatch objects are symmetrical.
    That is, if we only get the atoms and bonds in the mapping, the two molecules are identical.
    :param match1: The first SerializableMoleculeMatch object.
    :param match2: The second SerializableMoleculeMatch object.
    :return: True if the matches are symmetrical, False otherwise.
    """
    match1_test = match1.get_matched_molecule_copy()
    match1_atom_indexes = set(match1._query_atom_to_atom.values())
    match1_bond_indexes = set(match1._query_bond_to_bond.values())
    atom_delete_list: list[int] = []
    atom_mirror_list: list[int] = []
    bond_delete_list: list[int] = []
    bond_mirror_list: list[int] = []
    for atom in match1_test.iterateAtoms():
        if atom.index() not in match1_atom_indexes:
            atom_delete_list.append(atom.index())
        else:
            atom_mirror_list.append(atom.index())
    for bond in match1_test.iterateBonds():
        if bond.index() not in match1_bond_indexes:
            bond_delete_list.append(bond.index())
        else:
            bond_mirror_list.append(bond.index())
    match1_test.removeBonds(bond_delete_list)
    match1_test.removeAtoms(atom_delete_list)
    match1_mirror_test = match1.get_matched_molecule_copy()
    match1_mirror_test.removeBonds(bond_mirror_list)
    match1_mirror_test.removeAtoms(atom_mirror_list)

    match2_test = match2.get_matched_molecule_copy()
    match2_atom_indexes = set(match2._query_atom_to_atom.values())
    match2_bond_indexes = set(match2._query_bond_to_bond.values())
    atom_delete_list = []
    bond_delete_list = []
    atom_mirror_list = []
    bond_mirror_list = []
    for atom in match2_test.iterateAtoms():
        if atom.index() not in match2_atom_indexes:
            atom_delete_list.append(atom.index())
        else:
            atom_mirror_list.append(atom.index())
    for bond in match2_test.iterateBonds():
        if bond.index() not in match2_bond_indexes:
            bond_delete_list.append(bond.index())
        else:
            bond_mirror_list.append(bond.index())
    match2_test.removeBonds(bond_delete_list)
    match2_test.removeAtoms(atom_delete_list)
    match2_mirror_test = match2.get_matched_molecule_copy()
    match2_mirror_test.removeBonds(bond_mirror_list)
    match2_mirror_test.removeAtoms(atom_mirror_list)

    return match1_test.canonicalSmiles() == match2_test.canonicalSmiles() and \
        match1_mirror_test.canonicalSmiles() == match2_mirror_test.canonicalSmiles()
