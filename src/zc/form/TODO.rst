====
Todo
====

Tests::

  <content title= schema= fields= omit_fields= schemaprefix=
    >
    <require permission= attributes= interfaces=>
    <allow attributes= interfaces=>
    <add ...>
      <buttons ...>
        <button showDisabled= description=...>
      </buttons>
      <require ...>
      <allow ...>
      <macrotemplate name= source=>
      <menuItem .../>
      <widget .../>
    </add>
    <edit degradeInput= degradeDisplay= displayFields=>
      ...
      <schema prefix= source= fields= >
        <widget .../>
      </schema>
    </edit>
    <display degradeDisplay=>

    </display>
    <form degradeInput= degradeDisplay= displayFields= editFields=>
      ...
    </form>
    <menuItem ...>
  </content>

* Be able to specify some fields as input and others as display would be nice

* remove extra_script

* condition to show the form (and menu item) (e.g. condition="not:context/finalized_date")
