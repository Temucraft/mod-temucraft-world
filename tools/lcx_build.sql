set @maps = '960,1008,1136,1048';
-- spawns from LegionCore (they match its scripts), difficulty bits mapped to 3.3.5 (spawnMask is rewritten by convert.py)
create table lcx.creature like sf548.creature;
insert into lcx.creature (guid,id,map,spawnMask,phaseId,phaseGroup,modelid,equipment_id,position_x,position_y,position_z,orientation,spawntimesecs,spawndist,currentwaypoint,curhealth,curmana,MovementType,npcflag,unit_flags,dynamicflags)
select guid,id,map,spawnMask,0,0,modelid,equipment_id,position_x,position_y,position_z,orientation,spawntimesecs,spawndist,currentwaypoint,curhealth,curmana,MovementType,npcflag,unit_flags,dynamicflags
from legioncore_world.creature where map in (960,1008,1136,1048);
create table lcx.gameobject like sf548.gameobject;
insert into lcx.gameobject (guid,id,map,spawnMask,phaseId,phaseGroup,position_x,position_y,position_z,orientation,rotation0,rotation1,rotation2,rotation3,spawntimesecs,animprogress,state)
select guid,id,map,spawnMask,0,0,position_x,position_y,position_z,orientation,rotation0,rotation1,rotation2,rotation3,spawntimesecs,animprogress,state
from legioncore_world.gameobject where map in (960,1008,1136,1048);
create table lcx.creature_addon like sf548.creature_addon;
insert into lcx.creature_addon select a.* from legioncore_world.creature_addon a join lcx.creature c on c.guid=a.guid;
create table lcx.creature_formations like sf548.creature_formations;
insert ignore into lcx.creature_formations (leaderGUID,memberGUID,dist,angle,groupAI) select f.leaderGUID,f.memberGUID,f.dist,f.angle,f.groupAI from legioncore_world.creature_formations f join lcx.creature c on c.guid=f.leaderGUID;
create table lcx.waypoint_data like sf548.waypoint_data;
insert ignore into lcx.waypoint_data (id,point,position_x,position_y,position_z,orientation,delay,move_flag,action,action_chance,wpguid)
select w.id,w.point,w.position_x,w.position_y,w.position_z,w.orientation,w.delay,w.move_flag,w.action,w.action_chance,0 from legioncore_world.waypoint_data w where w.id in (select path_id from lcx.creature_addon where path_id>0);
insert ignore into lcx.waypoint_data select * from sf548.waypoint_data;
-- templates: SkyFire's where it has them, LegionCore's (+ wdb names/models) for the rest the maps and scripts need
create table lcx.need (e int primary key);
insert ignore into lcx.need select distinct id from lcx.creature;
insert ignore into lcx.need select e from lcx.want_npc;
insert ignore into lcx.need select entry from legioncore_world.creature_template where ScriptName in (select n from lcx.want_sn);
create table lcx.creature_template like sf548.creature_template;
insert into lcx.creature_template (entry,difficulty_entry_1,difficulty_entry_2,difficulty_entry_3,KillCredit1,KillCredit2,modelid1,modelid2,modelid3,modelid4,name,subname,IconName,gossip_menu_id,minlevel,maxlevel,exp,exp_unk,faction_A,faction_H,npcflag,speed_walk,speed_run,scale,npc_rank,mindmg,maxdmg,dmgschool,attackpower,dmg_multiplier,baseattacktime,rangeattacktime,unit_class,unit_flags,unit_flags2,dynamicflags,family,trainer_type,trainer_class,trainer_race,minrangedmg,maxrangedmg,rangedattackpower,type,type_flags,type_flags2,lootid,pickpocketloot,skinloot,resistance1,resistance2,resistance3,resistance4,resistance5,resistance6,spell1,spell2,spell3,spell4,spell5,spell6,spell7,spell8,PetSpellDataId,VehicleId,mingold,maxgold,AIName,MovementType,InhabitType,HoverHeight,Health_mod,Mana_mod,Mana_mod_extra,Armor_mod,RacialLeader,questItem1,questItem2,questItem3,questItem4,questItem5,questItem6,movementId,RegenHealth,mechanic_immune_mask,flags_extra,ScriptName,ModLevel,detection_range,WDBVerified)
select t.entry,0,0,0,w.KillCredit1,w.KillCredit2,w.Displayid1,w.Displayid2,w.Displayid3,w.Displayid4,w.Name1,w.Title,w.CursorName,t.gossip_menu_id,greatest(t.minlevel,t.ScaleLevelMin),greatest(t.maxlevel,t.ScaleLevelMax,t.minlevel,t.ScaleLevelMin),least(t.exp,4),0,t.faction,t.faction,t.npcflag,t.speed_walk,t.speed_run,t.scale,w.Classification,t.mindmg,t.maxdmg,t.dmgschool,t.attackpower,t.dmg_multiplier,t.baseattacktime,t.rangeattacktime,t.unit_class,t.unit_flags,t.unit_flags2,t.dynamicflags,w.Family,t.trainer_type,t.trainer_class,t.trainer_race,t.minrangedmg,t.maxrangedmg,t.rangedattackpower,w.Type,w.TypeFlags,w.TypeFlags2,0,0,0,t.resistance1,t.resistance2,t.resistance3,t.resistance4,t.resistance5,t.resistance6,t.spell1,t.spell2,t.spell3,t.spell4,t.spell5,t.spell6,t.spell7,t.spell8,t.PetSpellDataId,t.VehicleId,t.mingold,t.maxgold,t.AIName,t.MovementType,t.InhabitType,t.HoverHeight,w.HpMulti,w.PowerMulti,t.Mana_mod_extra,t.Armor_mod,w.Leader,w.QuestItem1,w.QuestItem2,w.QuestItem3,w.QuestItem4,w.QuestItem5,w.QuestItem6,w.MovementInfoID,t.RegenHealth,t.mechanic_immune_mask,t.flags_extra,t.ScriptName,0,20,0
from legioncore_world.creature_template t join legioncore_world.creature_template_wdb w on w.Entry=t.entry where t.entry in (select e from lcx.need);
insert ignore into lcx.creature_template select * from sf548.creature_template;
-- script names: LegionCore's wherever its script is one we ported
update lcx.creature_template c join legioncore_world.creature_template t on t.entry=c.entry set c.ScriptName=t.ScriptName where t.ScriptName in (select n from lcx.want_sn);
create table lcx.creature_template_addon like sf548.creature_template_addon;
insert into lcx.creature_template_addon select * from sf548.creature_template_addon;
insert ignore into lcx.creature_template_addon select * from legioncore_world.creature_template_addon where entry in (select e from lcx.need);
create table lcx.creature_equip_template like sf548.creature_equip_template;
insert into lcx.creature_equip_template select * from sf548.creature_equip_template;
insert ignore into lcx.creature_equip_template (entry,id,itemEntry1,itemEntry2,itemEntry3) select CreatureID,ID,ItemID1,ItemID2,ItemID3 from legioncore_world.creature_equip_template where CreatureID in (select e from lcx.need);
create table lcx.gneed (e int primary key);
insert ignore into lcx.gneed select distinct id from lcx.gameobject;
insert ignore into lcx.gneed select e from lcx.want_go;
insert ignore into lcx.gneed select entry from legioncore_world.gameobject_template where ScriptName in (select n from lcx.want_sn);
create table lcx.gameobject_template like sf548.gameobject_template;
insert into lcx.gameobject_template (entry,type,displayId,name,IconName,castBarCaption,unk1,faction,flags,size,questItem1,questItem2,questItem3,questItem4,questItem5,questItem6,data0,data1,data2,data3,data4,data5,data6,data7,data8,data9,data10,data11,data12,data13,data14,data15,data16,data17,data18,data19,data20,data21,data22,data23,data24,data25,data26,data27,data28,data29,data30,data31,unkInt32,AIName,ScriptName,WDBVerified)
select entry,type,displayId,name,IconName,castBarCaption,unk1,faction,flags,size,questItem1,questItem2,questItem3,questItem4,questItem5,questItem6,Data0,Data1,Data2,Data3,Data4,Data5,Data6,Data7,Data8,Data9,Data10,Data11,Data12,Data13,Data14,Data15,Data16,Data17,Data18,Data19,Data20,Data21,Data22,Data23,Data24,Data25,Data26,Data27,Data28,Data29,Data30,Data31,unkInt32,AIName,ScriptName,0
from legioncore_world.gameobject_template where entry in (select e from lcx.gneed);
insert ignore into lcx.gameobject_template select * from sf548.gameobject_template;
update lcx.gameobject_template g join legioncore_world.gameobject_template t on t.entry=g.entry set g.ScriptName=t.ScriptName where t.ScriptName in (select n from lcx.want_sn);
-- texts: LegionCore's (its group ids are the ones the scripts Talk() with), English from broadcast_text
create table lcx.creature_text like sf548.creature_text;
insert into lcx.creature_text select * from sf548.creature_text where entry not in (select distinct Entry from legioncore_world.creature_text where Entry in (select e from lcx.need));
-- loot and heroic entries stay SkyFire's where it has a real (non placeholder) row
update lcx.creature_template c join sf548.creature_template s on s.entry=c.entry set c.lootid=s.lootid, c.skinloot=s.skinloot, c.pickpocketloot=s.pickpocketloot, c.difficulty_entry_1=s.difficulty_entry_1, c.difficulty_entry_2=s.difficulty_entry_2, c.difficulty_entry_3=s.difficulty_entry_3 where c.entry in (select e from lcx.need) and s.minlevel>1;
update lcx.creature_template set family=0 where family>46 or family<0;
