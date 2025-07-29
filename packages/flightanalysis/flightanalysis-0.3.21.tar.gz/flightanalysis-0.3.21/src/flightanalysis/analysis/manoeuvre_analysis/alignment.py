from __future__ import annotations

from dataclasses import dataclass

from flightdata import State, align

from flightanalysis.definition import ManDef
from flightanalysis.elements import Element
from flightanalysis.manoeuvre import Manoeuvre

from ..el_analysis import ElementAnalysis
from .basic import Basic


@dataclass(repr=False)
class Alignment(Basic):
    manoeuvre: Manoeuvre | None
    templates: dict[str, State] | None

    @property
    def template(self):
        return State.stack(self.templates, "element")

    @property
    def template_list(self):
        return list(self.templates.values())

    def get_ea(self, name_or_id: str | int) -> ElementAnalysis:
        el: Element = self.manoeuvre.elements[name_or_id]
        fl = self.flown.element[el.uid]
        tp = self.templates[el.uid].relocate(fl.pos[0])
        return ElementAnalysis(
            self.mdef.eds[name_or_id],
            self.mdef.mps,
            el,
            fl,
            tp,
            tp[0].transform,
            self.scores.intra[name_or_id] if isinstance(self, Scored) else None
        )

    def __getattr__(self, name) -> ElementAnalysis:
        return self.get_ea(name)

    def __getitem__(self, name_or_id) -> ElementAnalysis:
        return self.get_ea(name_or_id)

    def __iter__(self):
        for edn in list(self.mdef.eds.data.keys()):
            yield self.get_ea(edn)

    def run_all(
        self, optimise_aligment=True, force=False
    ) -> Alignment | Complete | Scored:
        if self.__class__.__name__ == "Scored" and force:
            self = self.downgrade()
        while self.__class__.__name__ != "Scored":
            self = (
                self.run(optimise_aligment)
                if isinstance(self, Complete)
                else self.run()
            )
        return self

    @staticmethod
    def from_dict(ajman: dict) -> Alignment | Basic:
        basic = Basic.from_dict(ajman)
        if isinstance(basic, Basic) and "manoeuvre" in ajman and ajman["manoeuvre"]:
            manoeuvre = Manoeuvre.from_dict(ajman["manoeuvre"])

            trust_templates = (
                "templates" in ajman
                and ajman["templates"] is not None
                and set(ajman["templates"].keys())
                == set(
                    [el["uid"] for el in ajman["manoeuvre"]["elements"]] + ["exit_line"]
                )
            )

            return Alignment(
                **basic.__dict__,
                manoeuvre=manoeuvre,
                templates={k: State.from_dict(v) for k, v in ajman["templates"].items()}
                if trust_templates
                else manoeuvre.create_template(basic.create_itrans(), basic.flown),
            )
        return basic

    def to_dict(self, basic: bool = False) -> dict:
        _basic = super().to_dict(basic)
        if basic:
            return _basic
        return dict(
            **_basic,
            manoeuvre=self.manoeuvre.to_dict(),
            templates={k: tp.to_dict(True) for k, tp in self.templates.items()},
        )

    def run(self) -> Alignment | Complete:
        if "element" not in self.flown.labels.lgs:
            return self._run(True)[1]
        return self._run(False)[1].proceed()

    def _run(self, mirror=False, radius=10) -> Alignment:
        res = align(self.flown, self.template, radius, mirror)
        return res.dist, self.update(res.aligned)

    def update(self, aligned: State) -> Alignment:
        man, tps = self.manoeuvre.match_intention(self.template_list[0][0], aligned)
        mdef = self.mdef.update_defaults(man)
        return Alignment(self.id, self.schedule_direction, aligned, mdef, man, tps)

    def _proceed(self) -> Complete:
        if "element" in self.flown.labels.keys():
            correction = self.mdef.create()
            return Complete(
                self.id,
                self.schedule_direction,
                self.flown,
                self.mdef,
                self.manoeuvre,
                self.template,
                correction,
                correction.create_template(self.template[0], self.flown),
            )
        else:
            return self


from .complete import Complete  # noqa: E402
from .scored import Scored  # noqa: E402
