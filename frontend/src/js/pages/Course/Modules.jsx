import React from 'react';
import { Link } from 'react-router-dom';

import {
  TypeContestIcon,
  TypePageIcon,
  TypeTextIcon,
  TypeTriangleIcon,
} from '../../components/Icon';


const SectionModuleWrapper = ({ Icon, children }) => (
  <div className="sectionModule">
    <Icon size={18} />
    <div className="sectionModuleName">
      {children}
    </div>
  </div>
);


const BookModule = ({ book: { name, url }, ...props }) => (
  <SectionModuleWrapper Icon={TypeTextIcon} {...props}>
    <a href={url}>{name}</a>
  </SectionModuleWrapper>
)


const LabelModule = ({ key, label: { content } }) => (
  <div key={key} className="sectionModule">
    <TypeTextIcon size={18} />
    <div
      className="sectionModuleName"
      dangerouslySetInnerHTML={{__html: content}}
      style={{
        fontWeight: 'normal',
        color: 'black',
      }}
    />
  </div>
);


const MonitorModule = ({ monitor: { name, url } }, ...props) => (
  <SectionModuleWrapper Icon={TypePageIcon} {...props}>
    <a href={url}>{name}</a>
  </SectionModuleWrapper>
)


const ResourceModule = ({ resource: { name, reference }, ...props }) => (
  <SectionModuleWrapper Icon={TypePageIcon} {...props}>
    <a href={reference}>{name}</a>
  </SectionModuleWrapper>
);


const StatementModule = ({ statement: { id, name }, ...props }) => (
  <SectionModuleWrapper Icon={TypeContestIcon} {...props}>
    <Link to={`/contest/${id}`}>{name}</Link>
  </SectionModuleWrapper>
);


const SectionModule = ({ instance, type }) => {
  switch (type) {
    case 'BOOK':
      return <BookModule book={instance} />
    case 'LABEL':
      return <LabelModule label={instance} />
    case 'MONITOR':
      return <MonitorModule monitor={instance} />
    case 'RESOURCE':
      return <ResourceModule resource={instance} />
    case 'STATEMENT':
      return <StatementModule statement={instance} />
  }
  console.log('Найден неизвестный модуль');
  return null;
}


export default SectionModule;
